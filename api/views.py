from django.conf import settings
from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.documents.message import MessageDocument
from api.documents.utils import LoggingPageNumberPagination
from api.serializers import (
    AccountSerializer,
    MessageAuditSerializer,
    MessageDocumentSerializer,
    MessageSerializer,
    UserSerializer,
)
from core.models import Account, Message, User
from etl.tasks import import_file_task


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


class AccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: currently showing all accounts.
        # TODO: need to decide how/if to limit access
        accounts = Account.objects.all()
        serialized_account = AccountSerializer(accounts, many=True)
        return Response(serialized_account.data)

    def post(self, request):
        if request.data["title"] and request.data["filename"]:
            serialized_account = AccountSerializer(data=request.data)
            if serialized_account.is_valid():
                account = serialized_account.save()
                import_file_task.delay([request.data["filename"]], account.title)
                return Response(serialized_account.data, status=status.HTTP_201_CREATED)
            return Response(
                serialized_account.errors, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET", "PUT"])
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

    if request.method == "PUT":
        """
        We don't really edit messages-- this endpoint updates an associated MessageAudit
        """
        serialized_audit = MessageAuditSerializer(
            message.audit, data=request.data, partial=True
        )
        if serialized_audit.is_valid():
            serialized_audit.save(updated_by=request.user)
            return Response(serialized_audit.data)
        return Response(serialized_audit.errors, status=status.HTTP_400_BAD_REQUEST)


HIGHLIGHT_LABELS = {
    "pre_tags": ["<strong>"],
    "post_tags": ["</strong>"],
    "fragment_size": 40,
    "number_of_fragments": 5,
}


class MessageDocumentView(DocumentViewSet):
    """The MessageDocument view."""

    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

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
    if settings.ELASTICSEARCH_LOG_QUERIES:
        pagination_class = LoggingPageNumberPagination

    # Define search fields
    search_fields = (
        "msg_from",
        "msg_to",
        "subject",
        "body",
    )

    faceted_search_fields = {
        "processed": {
            "field": "audit.processed",
            "facet": TermsFacet,
            "enabled": True,
        },
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
        "account": "account.id",
        "sent_date": "sent_date",
        "msg_from": "msg_from",
        "body": "body",
        "processed": "audit.processed",
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
    }

    highlight_fields = {
        "body": {"enabled": True, "options": HIGHLIGHT_LABELS},
        "subject": {"enabled": True, "options": HIGHLIGHT_LABELS},
        "msg_to": {"options": HIGHLIGHT_LABELS},
        "msg_from": {"options": HIGHLIGHT_LABELS},
    }

    # Define ordering fields
    ordering_fields = {"_score": "_score", "sent_date": "sent_date"}
    # Specify default ordering
    ordering = ("-_score", "sent_date")
