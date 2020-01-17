from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import analyzer
from ratom.models import Message

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])
INDEX.settings(number_of_shards=1, number_of_replicas=1)

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


@INDEX.doc_type
class MessageDocument(Document):
    """Message Elasticsearch Document"""

    id = fields.IntegerField(attr="id")
    message_id = fields.TextField()
    msg_from = fields.TextField()
    msg_to = fields.TextField()
    subject = fields.TextField()
    headers = fields.TextField()
    body = fields.TextField()
    sent_date = fields.DateField()

    labels = fields.KeywordField(
        attr="labels_indexing",
        fields={
            "raw": fields.TextField(analyzer="keyword", multi=True),
            "suggest": fields.CompletionField(multi=True),
        },
        multi=True,
    )

    account = fields.NestedField(
        attr="account_indexing",
        properties={
            "title": fields.StringField(
                fields={
                    "raw": fields.KeywordField(),
                    "suggest": fields.CompletionField(),
                }
            )
        },
    )

    class Django(object):
        model = Message
        # True disables auto-indexing
        ignore_signals = True
