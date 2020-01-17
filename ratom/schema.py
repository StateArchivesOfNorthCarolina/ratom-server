from datetime import datetime
from elasticsearch_dsl import DateHistogramFacet
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_elastic import filter_backends
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)


from .models import User, Processor, Message, Account
from .documents import MessageDocument


HIGHLIGHT_TAGS = {
    "pre_tags": ["<strong>"],
    "post_tags": ["</strong>"],
}

# # # # # # # # # # # #
# # #   QUERIES   # # #
# # # # # # # # # # # #
class UserType(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        exclude = ("password",)


class CollectionType(DjangoObjectType):
    class Meta:
        model = Account
        interfaces = (relay.Node,)


class CollectionConnection(relay.Connection):
    class Meta:
        node = CollectionType


class MessageType(DjangoObjectType):
    labels = graphene.List(of_type=graphene.String)

    def resolve_labels(self, info):
        labels = []
        if self.data:
            labels = self.data.get("labels", [])
        return labels

    class Meta:
        model = Message
        exclude = ("data",)
        interfaces = (relay.Node,)


class MessageElasticsearchNode(ElasticsearchObjectType):
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

        # For `SearchFilterBackend` backend
        search_fields = {
            "msg_to": None,
            "msg_from": None,
            "msg_subject": None,
            "msg_body": None,
        }

        # For `FilteringFilterBackend` backend
        filter_fields = {
            "sent_date": "sent_date",
            "msg_from": "msg_from",
            "labels": "labels",
            "msg_body": "msg_body",
            "pk": "pk",
            # "processor": {} # TODO: NestedBackend does not exist in this library yet. Let's build it.
        }

        highlight_fields = {
            "msg_body": {"options": HIGHLIGHT_TAGS},
            "msg_subject": {"options": HIGHLIGHT_TAGS},
            "msg_to": {"options": HIGHLIGHT_TAGS},
            "msg_from": {"options": HIGHLIGHT_TAGS},
        }

        faceted_search_fields = {
            "labels": "labels",
            "sent_date": {
                "field": "sent_date",
                "facet": DateHistogramFacet,
                "options": {"interval": "year",},
            },
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
    message = graphene.Field(MessageType, pk=graphene.Int())
    filter_messages = ElasticsearchConnectionField(MessageElasticsearchNode)

    all_collections = relay.ConnectionField(CollectionConnection)
    my_collections = relay.ConnectionField(CollectionConnection)

    # @login_required
    def resolve_message(root, info, pk):
        return Message.objects.filter(pk=pk).first()

    # @login_required
    def resolve_filter_messages(root, info, *args, **kwargs):
        print(info.context.body)
        pass

    # @login_required
    def resolve_all_collections(root, info):
        return Collection.objects.all()

    # @login_required
    def resolve_my_collections(root, info):
        # TODO: restrict to collections user=info.context.user
        return Collection.objects.all()


# # # # # # # # # # # #
# # #  MUTATIONS  # # #
# # # # # # # # # # # #

# Override JSWONWebTokenMutation to provide User in response
class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class ProcessorType(DjangoObjectType):
    class Meta:
        model = Processor


class ProcessorMutation(graphene.Mutation):
    class Arguments:
        message_id = graphene.Int()
        processed = graphene.Boolean()
        is_record = graphene.Boolean()
        has_pii = graphene.Boolean()

    processor = graphene.Field(ProcessorType)

    @login_required
    def mutate(self, info, message_id, **kwargs):
        # args explicitly named above are required
        try:
            processor = Processor.objects.create(**kwargs)
            if kwargs.get("processed") == True:
                processor.date_processed = datetime.now()
            processor.date_modified = datetime.now()

            # ? so where is my request object? Where can I get the JWT??
            # Consider for JWT auth
            # https://github.com/flavors/django-graphql-jwt

            # processor.last_modified_by = info.context.user
            # see https://docs.graphene-python.org/projects/django/en/latest/authorization/#user-based-queryset-filtering

            processor.save()
            message = Message.objects.filter(pk=message_id).first()
            message.processor = processor
            message.save()
            return ProcessorMutation(processor=processor)
        except:
            raise Exception("Could not save Processor or Message")


class Mutation(graphene.ObjectType):
    create_processor = ProcessorMutation.Field()
