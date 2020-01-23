from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import DateHistogramFacet, RangeFacet, TermsFacet

from api.documents.message import MessageDocument
from core.models import User, Account, Message
from api.serializers import (
    UserSerializer,
    AccountSerializer,
    MessageSerializer,
    MessageDocumentSerializer,
)


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_detail(request, pk):
    """
    Retrieve a Message
    """
    try:
        message = Message.objects.get(pk=pk)
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serialized_message = MessageSerializer(message)
        return Response(serialized_message.data)


HIGHLIGHT_LABELS = {
    "pre_labels": ["<strong>"],
    "post_labels": ["</strong>"],
}


class MessageDocumentView(DocumentViewSet):
    """The MessageDocument view."""

    permission_classes = (IsAuthenticated,)

    document = MessageDocument
    serializer_class = MessageDocumentSerializer
    lookup_field = "id"
    filter_backends = [
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.CompoundSearchFilterBackend,
        filter_backends.FacetedSearchFilterBackend,
        filter_backends.HighlightBackend,
    ]

    # Define search fields
    search_fields = (
        "msg_from",
        "msg_to",
        "subject",
        "body",
    )

    faceted_search_fields = {
        "labels": {
            # "field": "labels.raw",
            "field": "labels",
            "facet": TermsFacet,
            # "enabled": True,
        },
        "sent_date": {
            "field": "sent_date",
            "facet": DateHistogramFacet,
            "options": {"interval": "year",},
        },
    }

    # Define filtering fields
    filter_fields = {
        "id": {
            "field": "_id",
            "lookups": [constants.LOOKUP_FILTER_RANGE, constants.LOOKUP_QUERY_IN,],
        },
        "labels": {
            "field": "labels",
            "lookups": [
                constants.LOOKUP_FILTER_TERMS,
                constants.LOOKUP_FILTER_PREFIX,
                constants.LOOKUP_FILTER_WILDCARD,
                constants.LOOKUP_QUERY_IN,
                constants.LOOKUP_QUERY_EXCLUDE,
            ],
        },
        "sent_date": "sent_date",
        "msg_from": "msg_from",
        "body": "body",
        "pk": "pk",
    }

    highlight_fields = {
        "body": {"options": HIGHLIGHT_LABELS},
        "subject": {"options": HIGHLIGHT_LABELS},
        "msg_to": {"options": HIGHLIGHT_LABELS},
        "msg_from": {"options": HIGHLIGHT_LABELS},
    }

    # Define ordering fields
    ordering_fields = {"sent_date": "sent_date"}
    # Specify default ordering
    ordering = ("sent_date",)
