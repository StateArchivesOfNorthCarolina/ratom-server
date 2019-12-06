import graphene

from graphene import Node, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from elasticsearch_dsl import DateHistogramFacet

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
    FacetedSearchFilterBackend,
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
        interfaces = (relay.Node,)
        filter_backends = [
            FilteringFilterBackend,
            SearchFilterBackend,
            FacetedSearchFilterBackend,
            HighlightFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]

        # For `FilteringFilterBackend` backend
        filter_fields = {
            "sent_date": "sent_date",
            "msg_from": "msg_from",
            "labels": "labels",
            "msg_body": "msg_body"
        }

        highlight_fields = {
            "msg_body": {
                # "enabled": True,
                "options": {"pre_tags": ["<strong>"], "post_tags": ["</strong>"],},
            },
            "msg_subject": {
                # "enabled": True,
                "options": {"pre_tags": ["<span>"], "post_tags": ["</span>"],},
            }
        }

        faceted_search_fields = {
            "labels": "labels",
            "sent_date": {
                "field": "sent_date",
                "facet": DateHistogramFacet,
                "options": {"interval": "year",},
            },
        }

        # For `SearchFilterBackend` backend
        search_fields = {
            "msg_body": {"boost": 4},
            "msg_subject": {"boost": 2},
            "msg_from": None,
            "sent_date": None,
        }

        # For `DefaultOrderingFilterBackend` backend
        ordering_defaults = (
            "_score",
            # "-sent_date",  # Field name in the Elasticsearch document
        )

        # For `OrderingFilterBackend` backend
        ordering_fields = {
            "sent_date": "sent_date",
        }



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
