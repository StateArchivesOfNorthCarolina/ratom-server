from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import analyzer
from core.models import Message

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])
INDEX.settings(number_of_shards=1, number_of_replicas=1)

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)

lowercase_analyzer = analyzer(
    "lowercase_analyzer", tokenizer="keyword", filter=["lowercase"]
)


@INDEX.doc_type
class MessageDocument(Document):
    """Message Elasticsearch Document"""

    id = fields.IntegerField(attr="id")
    source_id = fields.TextField(fielddata=True)
    msg_to = fields.StringField(analyzer=lowercase_analyzer)
    msg_from = fields.StringField(analyzer=lowercase_analyzer)
    subject = fields.TextField(analyzer=html_strip)
    body = fields.TextField(analyzer=html_strip)
    sent_date = fields.DateField()
    labels = fields.NestedField(
        attr="labels_indexing",
        properties={
            "importer": fields.NestedField(
                properties={"name": fields.StringField()}, multi=True
            ),
        }
        # attr="labels_indexing",
        # fields={
        #     "raw": fields.KeywordField(multi=True),
        #     "suggest": fields.CompletionField(multi=True),
        # },
        # multi=True,
    )

    audit = fields.ObjectField(
        properties={
            "processed": fields.BooleanField(),
            "is_record": fields.BooleanField(),
            "is_restricted": fields.BooleanField(),
            "needs_redaction": fields.BooleanField(),
        }
    )

    account = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "title": fields.StringField(
                fields={
                    "raw": fields.KeywordField(),
                    "suggest": fields.CompletionField(),
                }
            ),
        },
    )

    class Django(object):
        model = Message
