from django.conf import settings
from azure.storage.blob import BlobServiceClient
import io
from etl.providers.base import ImportProvider, ImportProviderError

import logging

logger = logging.getLogger(__name__)


class AzureServiceProvider(ImportProvider):
    """
    An import provider for RATOM instances that will use the AZURE platform for hosting of
    their pst files.

    :keyword:
       file_path (str) -- a string representing the path on the blob_store with the target file as
       the final part.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._data = None
        self.account_url = settings.AZURE_URL
        self.container = settings.AZURE_CONTAINER
        self.pst_blob_name = kwargs.get("file_path", "")
        self._service = None
        self._client = None
        self.pst_blob = None
        self.valid = True

    def _validate(self) -> bool:
        for b in self._client.list_blobs():
            if b.name == self.pst_blob_name:
                self.pst_blob = b
                return True
        return False

    def _get_file(self):
        self.blob_data = self._client.download_blob(self.pst_blob)
        self._data = io.BytesIO(self.blob_data.content_as_bytes())

    def open(self):
        self._service = BlobServiceClient(
            account_url=self.account_url, credential=settings.AZURE_BLOB_KEY
        )
        self._client = self._service.get_container_client(self.container)
        self.valid = self._validate()
        if not self.valid:
            raise ImportProviderError(
                message="File was not found", error="AzureServiceProviderError"
            )
        self._get_file()
        super().open()

    @property
    def path(self):
        return self.pst_blob_name

    @property
    def exists(self):
        return True

    @property
    def file_size(self):
        return self.blob_data.size

    @property
    def file_name(self):
        return self.pst_blob_name
