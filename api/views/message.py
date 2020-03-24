from django_elasticsearch_dsl_drf import filter_backends
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.documents.message import MessageDocument
from api.filter_backends import CustomFilteringFilterBackend
from api.serializers import (
    MessageAuditSerializer,
    MessageDocumentSerializer,
    MessageSerializer,
)
from api.views.utils import LoggingDocumentViewSet
from core.models import Message, MessageAudit

__all__ = ("message_detail", "messages_batch", "MessageDocumentView")


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
            serialized_message = MessageSerializer(message)
            return Response(serialized_message.data, status=status.HTTP_201_CREATED)
        return Response(serialized_audit.errors, status=status.HTTP_400_BAD_REQUEST)


# Actions
RECORD_STATUS = "record_status"
ALLOWED_ACTIONS = [RECORD_STATUS]

# Effects
OPEN_RECORD = "open_record"
NON_RECORD = "non-record"
REDACTED = "redacted"
RESTRICTED = "restricted"
ALLOWED_EFFECTS_BY_ACTION = {
    RECORD_STATUS: [OPEN_RECORD, NON_RECORD, REDACTED, RESTRICTED]
}


def get_data_from_record_status(audits, effect):
    if effect == OPEN_RECORD:
        effect_args = {
            "is_record": True,
            "is_restricted": False,
            "needs_redaction": False,
        }
    if effect == NON_RECORD:
        effect_args = {
            "is_record": False,
            "is_restricted": False,
            "needs_redaction": False,
        }
    if effect == REDACTED:
        effect_args = {
            "is_record": True,
            "is_restricted": False,
            "needs_redaction": True,
        }
    if effect == RESTRICTED:
        effect_args = {
            "is_record": True,
            "is_restricted": True,
            "needs_redaction": False,
        }
    return [{"id": a.pk, **effect_args} for a in audits]


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def messages_batch(request):
    if request.method == "PUT":
        """
        Performs a single action on a batch of messages
        """
        REQUIRED_DATA = ["messages", "action", "effect"]

        if None in [request.data.get(d) for d in REQUIRED_DATA]:
            return Response(
                {"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST
            )

        action = request.data.get("action")
        if action not in ALLOWED_ACTIONS:
            return Response(
                {"error": f"'{action}' is not a permitted action"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        effect = request.data.get("effect")
        if effect not in ALLOWED_EFFECTS_BY_ACTION[action]:
            return Response(
                {
                    "error": f"'{effect}' is not a permitted effect for action '{action}'"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == RECORD_STATUS:
            audits = MessageAudit.objects.filter(
                message__pk__in=request.data.get("messages")
            )
            data = get_data_from_record_status(audits, effect)
            serialized_audits = MessageAuditSerializer(
                data=data, instance=audits, many=True, partial=True
            )
            if serialized_audits.is_valid():
                serialized_audits.save(updated_by=request.user)
                return Response(serialized_audits.data, status=status.HTTP_201_CREATED)
            return Response(
                serialized_audits.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)


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
        "default_operator": "or",
    }

    faceted_search_fields = {
        "processed": {
            "field": "audit.processed",
            "facet": TermsFacet,
            "enabled": True,
        },
        "is_record": {
            "field": "audit.is_record",
            "facet": TermsFacet,
            "enabled": True,
        },
        "is_restricted": {
            "field": "audit.is_restricted",
            "facet": TermsFacet,
            "enabled": True,
        },
        "needs_redaction": {
            "field": "audit.needs_redaction",
            "facet": TermsFacet,
            "enabled": True,
        },
        "labels": {
            # "field": "labels.raw",
            "field": "labels",
            "facet": TermsFacet,
            # "enabled": True,
        },
        "is_record": {
            "field": "audit.is_record",
            "facet": TermsFacet,
            "enabled": True,
        },
        "is_restricted": {
            "field": "audit.is_restricted",
            "facet": TermsFacet,
            "enabled": True,
        },
        "needs_redaction": {
            "field": "audit.needs_redaction",
            "facet": TermsFacet,
            "enabled": True,
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
        "needs_redaction": "audit.needs_redaction",
        "is_restricted": "audit.is_restricted",
        "is_record": "audit.is_record",
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
