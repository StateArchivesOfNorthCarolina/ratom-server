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
    msg_to = fields.StringField()
    msg_from = fields.StringField()
    subject = fields.TextField(analyzer=html_strip)
    body = fields.TextField(analyzer=html_strip)
    sent_date = fields.DateField()
    directory = fields.KeywordField()

    audit = fields.ObjectField(
        properties={
            "processed": fields.BooleanField(),
            "is_record": fields.BooleanField(),
            "is_restricted": fields.BooleanField(),
            "needs_redaction": fields.BooleanField(),
            "labels": fields.NestedField(
                properties={
                    "type": fields.StringField(fields={"raw": fields.KeywordField()}),
                    "name": fields.StringField(fields={"raw": fields.KeywordField()}),
                },
                multi=True,
            ),
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

    file = fields.ObjectField(
        properties={"filename": fields.StringField(), "sha256": fields.StringField(),},
    )

    class Django(object):
        model = Message
