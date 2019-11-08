import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Collection, Processor, Message

class CollectionNode(DjangoObjectType):
    class Meta:
        model = Collection
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "accession_date": ["exact", "gte", "lte"]
        }
        interfaces = (relay.Node, )


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            "message_id": ["exact", "icontains", "istartswith"],
            "sent_date": ["exact", "icontains", "istartswith"],
            "msg_from": ["exact", "icontains", "istartswith"],
            "msg_to": ["exact", "icontains", "istartswith"],
            "msg_subject": ["exact", "icontains", "istartswith"],
        }
        interfaces = (relay.Node, )


class Query(object):
    collection = relay.Node.Field(CollectionNode)
    all_collections = DjangoFilterConnectionField(CollectionNode)
    message = relay.Node.Field(MessageNode)
    all_messages = DjangoFilterConnectionField(MessageNode)
