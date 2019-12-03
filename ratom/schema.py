import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    HighlightFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
)


from .models import Collection, Processor, Message
from .documents import MessageDocument


class CollectionNode(DjangoObjectType):
    class Meta:
        model = Collection
        filter_fields = {
            "title": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "accession_date": ["exact", "iexact", "icontains", "gte", "lte", "range"],
        }
        interfaces = (relay.Node,)


class MessageNode(ElasticsearchObjectType):
    class Meta:
        document = MessageDocument
        interfaces = (relay.Node,)
        filter_backends = [
            FilteringFilterBackend,
            SearchFilterBackend,
            HighlightFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]

        # For `FilteringFilterBackend` backend
        filter_fields = {
            # The dictionary key (in this case `title`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value could be simple or complex structure (in this case
            # complex). The `field` key points to the `title.raw`, which
            # is the field name in the Elasticsearch document
            # (`PostDocument`). Since `lookups` key is provided, number
            # of lookups is limited to the given set, while term is the
            # default lookup (as specified in `default_lookup`).
            "Sender": {
                "field": "msg_from",
                # Available lookups
                "lookups": [
                    LOOKUP_FILTER_TERM,
                    LOOKUP_FILTER_TERMS,
                    LOOKUP_FILTER_PREFIX,
                    LOOKUP_FILTER_WILDCARD,
                    LOOKUP_QUERY_IN,
                    LOOKUP_QUERY_EXCLUDE,
                ],
                # Default lookup
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            # The dictionary key (in this case `category`) is the name of
            # the corresponding GraphQL query argument. Since no lookups
            # or default_lookup is provided, defaults are used (all lookups
            # available, term is the default lookup). The dictionary value
            # (in this case `category.raw`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            # "category": "category",
            # The dictionary key (in this case `tags`) is the name of
            # the corresponding GraphQL query argument. Since no lookups
            # or default_lookup is provided, defaults are used (all lookups
            # available, term is the default lookup). The dictionary value
            # (in this case `tags.raw`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            "NER Tags": "labels",
            # The dictionary key (in this case `num_views`) is the name of
            # the corresponding GraphQL query argument. Since no lookups
            # or default_lookup is provided, defaults are used (all lookups
            # available, term is the default lookup). The dictionary value
            # (in this case `num_views`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            # "num_views": "num_views",
        }

        # For `SearchFilterBackend` backend
        search_fields = {
            "msg_body": {"boost": 4},
            "msg_subject": {"boost": 2},
            "msg_from": None,
        }

        # For `OrderingFilterBackend` backend
        ordering_fields = {
            # The dictionary key (in this case `tags`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value (in this case `tags.raw`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            "Message Sent": "sent_date",
            # The dictionary key (in this case `created_at`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value (in this case `created_at`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            # "created_at": "created_at",
            # The dictionary key (in this case `num_views`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value (in this case `num_views`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            # "num_views": "num_views",
        }

        # For `DefaultOrderingFilterBackend` backend
        ordering_defaults = (
            "-sent_date",  # Field name in the Elasticsearch document
            # "title.raw",  # Field name in the Elasticsearch document
        )

        # For `HighlightFilterBackend` backend
        highlight_fields = {
            "msg_subject": {
                "enabled": True,
                "options": {"pre_tags": ["<b>"], "post_tags": ["</b>"],},
            },
            "msg_body": {
                "options": {
                    "fragment_size": 50,
                    "number_of_fragments": 1,
                    "pre_tags": ["<b>"],
                    "post_tags": ["</b>"],
                }
            },
        }


class Query(ObjectType):
    # import pudb

    # pudb.set_trace()
    all_messages = ElasticsearchConnectionField(MessageNode)
