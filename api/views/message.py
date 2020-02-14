from django.conf import settings
from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.documents.message import MessageDocument
from api.documents.utils import LoggingPageNumberPagination
from core.models import Message
from api.serializers import (
    MessageAuditSerializer,
    MessageDocumentSerializer,
    MessageSerializer,
)

__all__ = ("message_detail", "MessageDocumentView")


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
        serialized_audit = MessageAuditSerializer(message.audit, data=request.data)
        if serialized_audit.is_valid():
            serialized_audit.save(updated_by=request.user)
            return Response(serialized_audit.data, status=status.HTTP_201_CREATED)
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
