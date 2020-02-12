import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from celery.exceptions import OperationalError

from api.serializers import AccountSerializer, UserSerializer, FileSerializer
from core.models import Account, User
from etl.tasks import import_file_task

__all__ = ("user_detail", "AccountListView", "account_detail")

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """
    Show details of single user
    """
    user_pk = request.user.pk
    user = User.objects.get(pk=user_pk)

    if request.method == "GET":
        serialized_user = UserSerializer(user)
        return Response(serialized_user.data)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def account_detail(request, pk):
    """
    Retrieve, update or delete an Account.
    """
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serialized_account = AccountSerializer(account)
        return Response(serialized_account.data)

    elif request.method == "PUT":
        serialized_file = FileSerializer(data=request.data)
        if serialized_file.is_valid():
            try:
                import_file_task.delay(
                    [serialized_file.validated_data["filename"]], account.title
                )
                return Response(status=status.HTTP_204_NO_CONTENT)
            except OperationalError as e:
                logger.warning(f"{e}")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serialized_file.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: currently showing all accounts.
        # TODO: need to decide how/if to limit access
        accounts = Account.objects.all()
        serialized_account = AccountSerializer(accounts, many=True)
        return Response(serialized_account.data, status=status.HTTP_200_OK)

    def post(self, request):
        serialized_account = AccountSerializer(data=request.data)
        if serialized_account.is_valid():
            serialized_file = FileSerializer(data=request.data)
            if serialized_file.is_valid():
                try:
                    import_file_task.delay(
                        [serialized_file.validated_data["filename"]],
                        serialized_account.validated_data["title"],
                    )
                    return Response(status=status.HTTP_204_NO_CONTENT)
                except OperationalError as e:
                    logger.warning(f"{e}")
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serialized_file.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialized_account.errors, status=status.HTTP_400_BAD_REQUEST)
