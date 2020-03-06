from django_elasticsearch_dsl_drf import filter_backends
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.documents.message import MessageDocument
from api.serializers import (
    MessageAuditSerializer,
    MessageDocumentSerializer,
    MessageSerializer,
)
from api.views.utils import LoggingDocumentViewSet
from api.filter_backends import CustomFilteringFilterBackend
from core.models import Message, Label

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
        if "label" in request.data:
            label = request.data["label"]
            lb, _ = Label.objects.get_or_create(**label)
            if lb not in message.audit.labels.all():
                message.audit.labels.add(lb)
                message.audit.save()
                message.save()
            serialized_message = MessageSerializer(message)
            return Response(serialized_message.data, status=status.HTTP_201_CREATED)
        else:
            serialized_audit = MessageAuditSerializer(
                message.audit, data=request.data, partial=True
            )
            if serialized_audit.is_valid():
                serialized_audit.save(updated_by=request.user)
                serialized_message = MessageSerializer(message)
                return Response(serialized_message.data, status=status.HTTP_201_CREATED)
            return Response(serialized_audit.errors, status=status.HTTP_400_BAD_REQUEST)


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
        CustomFilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.CompoundSearchFilterBackend,
        filter_backends.FacetedSearchFilterBackend,
        filter_backends.HighlightBackend,
        filter_backends.SimpleQueryStringSearchFilterBackend,
        filter_backends.NestedFilteringFilterBackend,
    ]

    # Define search fields
    search_fields = ("msg_from", "msg_to")

    simple_query_string_search_fields = {"subject": None, "body": None}

    simple_query_string_options = {
        "default_operator": "and",
    }

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
        "email": "msg_to",
        "body": "body",
        "processed": "audit.processed",
    }

    nested_filter_fields = {
        "labels_importer": {"field": "audit.labels.name.raw", "path": "audit.labels"},
    }

    highlight_fields = {
        "body": {"enabled": True, "options": HIGHLIGHT_LABELS},
        "subject": {"enabled": True, "options": HIGHLIGHT_LABELS},
        "msg_from": {"options": HIGHLIGHT_LABELS},
        "msg_to": {"options": HIGHLIGHT_LABELS},
    }

    # Define ordering fields
    ordering_fields = {
        "_score": "_score",
        "sent_date": "sent_date",
        "source_id": "source_id",
    }
    # Specify default ordering
    ordering = ("-_score", "sent_date", "source_id")
