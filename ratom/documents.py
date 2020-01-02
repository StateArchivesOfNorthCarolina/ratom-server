from typing import List

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Message, Processor


@registry.register_document
class MessageDocument(Document):
    pk = fields.IntegerField()
    labels = fields.KeywordField(multi=True)
    collection = fields.NestedField(
        properties={"title": fields.TextField(), "accession_date": fields.DateField()}
    )
    processor = fields.NestedField(
        properties={
            "processed": fields.BooleanField(),
            "is_record": fields.BooleanField(),
            "has_pii": fields.BooleanField(),
            "date_processed": fields.DateField(),
            "date_modified": fields.DateField(),
        }
    )

    # def prepare_id(self, instance):
    #     return instance.id

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
            "id",
            "msg_to",
            "msg_from",
            "msg_subject",
            "msg_body",
            "directory",
            "sent_date",
        ]

    # Ignore auto updating of Elasticsearch when a model is saved
    # or deleted:
    ignore_signals = True

    # Don't perform an index refresh after every update (overrides global setting):
    auto_refresh = False

    # Paginate the django queryset used to populate the index with the specified size
    # (by default it uses the database driver's default setting)
    # queryset_pagination = 5000


@registry.register_document
class ProcessorDocument(Document):
    class Index:
        name = "processor"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Processor

        fields = [
            "processed",
            "is_record",
            "has_pii",
            "date_processed",
            "date_modified",
        ]


######################################################

# from datetime import datetime
# from elasticsearch_dsl import (
#     Document,
#     Date,
#     Nested,
#     Boolean,
#     analyzer,
#     InnerDoc,
#     Completion,
#     Keyword,
#     Text,
#     Integer
# )

# from .models import Message

# html_strip = analyzer(
#     "html_strip",
#     tokenizer="standard",
#     filter=["standard", "lowercase", "stop", "snowball"],
#     char_filter=["html_strip"],
# )

# # class NestedUser(InnerDoc):
# #     user_type = Text()

# class NestedCollection(InnerDoc):
#     title = Text()
#     accession_date = Date()

#     def age(self):
#         return datetime.now() - self.accession_date

# class NestedProcessor(InnerDoc):
#     processed = Boolean()
#     is_record = Boolean()
#     has_pii = Boolean()
#     date_processed =  Date()
#     date_modified =  Date()
#     # last_modified_by =  Nested(NestedUser)

# class MessageDocument(Document):
# msg_from = Text()
# msg_subject = Text()
# msg_body = Text()
# directory = Text()
# sent_date = Date()
# labels = Keyword()
# #Text(fields={"raw": Keyword()})
# collection = Nested(NestedCollection)
# processor = Nested(NestedProcessor)

#     class Index:
#         name = "message"
