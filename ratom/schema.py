import graphene

from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField

from .models import Collection, Processor, Message

class CollectionType(DjangoObjectType):
    class Meta: 
        model = Collection
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "accessionDate": ["exact", "gte", "lte"]
        }


class Query(object):
    collection = graphene.Field(CollectionType, id=graphene.ID(), title=graphene.String(), accession_date=graphene.Date())
    all_collections = graphene.List(CollectionType)

    def resolve_collection(self, info, **kwargs):
        id = kwargs.get("id")
        title = kwargs.get("title")
        accession_date = kwargs.get("accession_date")
        
        import pdb; pdb.set_trace()

        if id is not None:
            return Collection.objects.get(pk=id)
        
        if title is not None:
            return Collection.objects.get(title=title)

        if accession_date is not None:
            return Collection.objects.get(accession_date=accession_date)

        return None

    def resolve_all_collections(self, info, **kwargs):
        return Collection.objects.all()
