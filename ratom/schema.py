import graphene

from graphene import Node
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


# class CollectionNode(DjangoObjectType):
#     class Meta:
#         model = Collection
#         filter_fields = {
#             "title": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
#             "accession_date": ["exact", "iexact", "icontains", "gte", "lte", "range"],
#         }
#         interfaces = (Node,)


class MessageNode(ElasticsearchObjectType):
    class Meta:
        document = MessageDocument
        interfaces = (Node,)
        filter_backends = [
            FilteringFilterBackend,
            SearchFilterBackend,
            # HighlightFilterBackend,
            # OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]

        # For `FilteringFilterBackend` backend
        filter_fields = {
            "msg_from": {
                "field": "msg_from",
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
            "labels": "labels",
        }

        # For `SearchFilterBackend` backend
        search_fields = {
            "msg_body": {"boost": 4},
            "msg_subject": {"boost": 2},
            "msg_from": None,
        }

        # For `OrderingFilterBackend` backend
        # ordering_fields = {
        #     "Message Sent": "sent_date",
        # }

        # For `DefaultOrderingFilterBackend` backend
        # ordering_defaults = (
        #     "-sent_date",  # Field name in the Elasticsearch document
        # )

        # For `HighlightFilterBackend` backend
        # highlight_fields = {
        #     "msg_subject": {
        #         "enabled": True,
        #         "options": {"pre_tags": ["<b>"], "post_tags": ["</b>"],},
        #     },
        #     "msg_body": {
        #         "options": {
        #             "fragment_size": 50,
        #             "number_of_fragments": 1,
        #             "pre_tags": ["<b>"],
        #             "post_tags": ["</b>"],
        #         }
        #     },
        # }


class Query(graphene.ObjectType):
    all_messages = ElasticsearchConnectionField(MessageNode)


"""
example query:

query {
  allMessages(
		search:{query:"Thompson"}
        # filter: {labels: {terms: ["PERSON", "MONEY"]}}
  ) {
    edges {
      node {
        msgFrom
        # msgSubject
        # msgBody
        directory
        labels
        collection
      }
    }
  }
}
"""
