from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import AccountSerializer, UserSerializer
from core.models import Account, User

__all__ = ("user_detail", "account_list", "account_detail")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """
    Show details of single user
    """
    try:
        user_pk = request.user.pk
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serialized_user = UserSerializer(user)
        return Response(serialized_user.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def account_list(request):
    """
    List all Accounts, or create a new Account.
    """
    if request.method == "GET":
        # TODO: currently showing all accounts.
        # TODO: need to decide how/if to limit access
        accounts = Account.objects.all()
        serialized_account = AccountSerializer(accounts, many=True)
        return Response(serialized_account.data)

    if request.method == "POST":
        serialized_account = AccountSerializer(data=request.data)
        if serialized_account.is_valid():
            serialized_account.save()
            return Response(serialized_account.data, status=status.HTTP_201_CREATED)
        return Response(serialized_account.errors, status=status.HTTP_400_BAD_REQUEST)


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
        serialized_account = AccountSerializer(account, data=request.data)
        if serialized_account.is_valid():
            serialized_account.save()
            return Response(serialized_account.data)
        return Response(serialized_account.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
