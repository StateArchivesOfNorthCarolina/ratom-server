from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from api.documents.utils import LoggingSearch


class LoggingDocumentViewSet(DocumentViewSet):
    """DocumentViewSet extension that instantiates LoggingSearch to perform optional logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search = LoggingSearch(
            using=self.client, index=self.index, doc_type=self.document._doc_type.name
        )
