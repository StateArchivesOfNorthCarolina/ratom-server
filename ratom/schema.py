from datetime import datetime
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id
from elasticsearch_dsl import DateHistogramFacet
from graphene_elastic import filter_backends
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)

from .models import Processor, Message
from .documents import MessageDocument

# # # # # # # # # # # # 
# # #   QUERIES   # # # 
# # # # # # # # # # # # 

class MessageNode(ElasticsearchObjectType):
    class Meta:
        document = MessageDocument
        interfaces = (graphene.relay.Node,)
        filter_backends = [
            filter_backends.FilteringFilterBackend,
            filter_backends.SearchFilterBackend,
            filter_backends.HighlightFilterBackend,
            filter_backends.OrderingFilterBackend,
            filter_backends.DefaultOrderingFilterBackend,
            filter_backends.FacetedSearchFilterBackend,
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


# # # # # # # # # # # # 
# # #  MUTATIONS  # # # 
# # # # # # # # # # # # 
class ProcessorType(DjangoObjectType):
    class Meta:
        model = Processor

class ProcessorMutation(graphene.Mutation):
    class Arguments:
        # ? so where is my request object? Where can I get the JWT??
        message_id = graphene.ID()
        processed = graphene.Boolean()
        is_record = graphene.Boolean()
        has_pii = graphene.Boolean()
        # date_processed = graphene.Date()
        # date_modified = graphene.Date()
        # processor_data = ProcessorInput()

    processor = graphene.Field(ProcessorType)

    def mutate(self, info, message_id, **kwargs):
        # Arguments explicitly named above are required
        try:
            processor = Processor.objects.create(**kwargs)
            if (kwargs.get('processed') == True):
                processor.date_processed = datetime.now()
            processor.date_modified = datetime.now()

            # Consider for JWT auth
            # https://github.com/flavors/django-graphql-jwt

            # processor.last_modified_by = info.context.user
            # see https://docs.graphene-python.org/projects/django/en/latest/authorization/#user-based-queryset-filtering

            processor.save()
            _, message_pk = from_global_id(message_id)
            import pdb; pdb.set_trace()
            message = Message.objects.filter(pk=message_pk).first()
            message.processor = processor
            message.save()
            return ProcessorMutation(processor=processor)
        except:
            raise Exception("Could not save Processor or Message")
# class ProcessorInput(graphene.InputObjectType):
#     # pass
#     processed = graphene.Boolean()
#     is_record = graphene.Boolean()
#     has_pii = graphene.Boolean()
#     date_processed = graphene.Date()
#     date_modified = graphene.Date()
#     # last_modified_by = graphene.ObjectType()

# class CreateProcessor(graphene.Mutation):
    # class Arguments:
    #     message_id = graphene.ID()
    #     processor_data = ProcessorInput()

#     processor = graphene.Field(ProcessorType)
#     Output = Processor

#     @staticmethod
#     def mutate(root, info, message_id, processor_data=None):
#         node, message_pk = from_global_id(message_id)
#         message = Message.objects.filter(pk=message_pk).first()
#         if message:
#             try:
#                 # TODO: set date processed and date_modified to now, conditionally
#                 created_processor = ProcessorType(**processor_data)
#                 created = CreateProcessor(processor=created_processor)
#                 message.processor = created_processor
#                 # message.save()
#             except:
#                 return Exception("Couldn't create processor")

#             # return CreateProcessor(ok=ok, processor=processor)


class Mutation(graphene.ObjectType):
    create_processor = ProcessorMutation.Field()
