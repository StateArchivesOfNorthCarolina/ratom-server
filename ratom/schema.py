import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Collection, Processor, Message

class CollectionNode(DjangoObjectType):
    class Meta:
        model = Collection
        filter_fields = {
            "title": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "sent_date": ["exact", "iexact", "icontains", "gte", "lte", "range"],
        }
        interfaces = (relay.Node, )


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            "message_id": ["exact", "iexact", "icontains", "istartswith"],
            "sent_date": ["exact", "iexact", "icontains", "gte", "lte", "range"],
            "msg_from": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "msg_to": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "msg_cc": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "msg_bcc": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
            "msg_subject": ["exact", "iexact", "icontains", "istartswith"],
            "msg_body": ["exact", "iexact", "icontains", "istartswith", "iendswith"],
        }
        interfaces = (relay.Node, )


class Query(object):
    collection = relay.Node.Field(CollectionNode)
    all_collections = DjangoFilterConnectionField(CollectionNode)
    message = relay.Node.Field(MessageNode)
    all_messages = DjangoFilterConnectionField(MessageNode)
