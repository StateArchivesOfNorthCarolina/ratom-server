from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import AccountSerializer, UserSerializer, FileSerializer
from core.models import Account, User
from etl.tasks import import_file_task

__all__ = ("user_detail", "AccountListView", "account_detail")


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
            import_file_task.delay(
                [serialized_file.validated_data["filename"]], account.title
            )
            return Response(serialized_file.data, status=status.HTTP_201_CREATED)
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
        return Response(serialized_account.data)

    def post(self, request):
        serialized_file = FileSerializer(data=request.data)
        if serialized_file.is_valid():
            serialized_account = AccountSerializer(data=request.data)
            if serialized_account.is_valid():
                account = serialized_account.save()
                import_file_task.delay(
                    [serialized_file.validated_data["filename"]], account.title
                )
                return Response(serialized_file.data, status=status.HTTP_200_OK)
        return Response(serialized_file.errors, status=status.HTTP_400_BAD_REQUEST)
