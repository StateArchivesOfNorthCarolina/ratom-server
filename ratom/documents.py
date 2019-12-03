from typing import List

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Message


@registry.register_document
class MessageDocument(Document):
    collection = fields.ObjectField(
        properties={"title": fields.TextField(), "accession_date": fields.DateField()}
    )
    labels = fields.KeywordField(multi=True)

    def prepare_labels(self, instance: Message) -> List[str]:
        labels: List[str] = []
        if instance.data:
            labels = list(instance.data.get("labels", []))
        return labels

    class Index:
        # Name of the Elasticsearch index
        name = "message"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Message  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            "msg_from",
            "msg_subject",
            "msg_body",
            "directory",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
