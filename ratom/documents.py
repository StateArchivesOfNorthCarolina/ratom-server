from datetime import datetime
from elasticsearch_dsl import (
    Document,
    Date,
    Nested,
    Boolean,
    analyzer,
    InnerDoc,
    Completion,
    Keyword,
    Text,
    Integer
)

from .models import Message

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)

class NestedUser(InnerDoc):
    user_type = Text()

class NestedCollection(InnerDoc):
    title = Text()
    accession_date = Date()

    def age(self):
        return datetime.now() - self.accession_date

class NestedProcessor(InnerDoc):
    processed = Boolean()
    is_record = Boolean()
    has_pii = Boolean()
    date_processed =  Date()
    date_modified =  Date()
    last_modified_by =  Nested(NestedUser)


class MessageDocument(Document):
    id = Integer() # ? This?
    msg_from = Text()
    msg_subject = Text()
    msg_body = Text()
    directory = Text()
    sent_date = Date()
    labels = Keyword()
    #Text(fields={"raw": Keyword()})
    collection = Nested(NestedCollection)
    processor = Nested(NestedProcessor)

    class Index:
        name = "message"

