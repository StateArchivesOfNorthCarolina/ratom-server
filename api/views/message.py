from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from elasticsearch_dsl import DateHistogramFacet, TermsFacet

from api.documents.message import MessageDocument
from core.models import Message
from api.serializers import (
    MessageSerializer,
    MessageDocumentSerializer,
)
from api.views.utils import LoggingDocumentViewSet

__all__ = ("message_detail", "MessageDocumentView")


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
    "pre_tags": ["<strong>"],
    "post_tags": ["</strong>"],
    "fragment_size": 40,
    "number_of_fragments": 5,
}


class MessageDocumentView(LoggingDocumentViewSet):
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
            "enabled": True,
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
    ordering_fields = {"_score": "_score"}
    # Specify default ordering
    ordering = ("-_score",)
