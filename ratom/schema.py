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


class Query(object):
    collection = relay.Node.Field(CollectionNode)
    all_collections = DjangoFilterConnectionField(CollectionNode)
