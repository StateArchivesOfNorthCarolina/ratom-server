from django.conf import settings
from azure.storage.blob import BlobServiceClient
from pathlib import Path
from etl.providers.base import ImportProvider
from tempfile import NamedTemporaryFile
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
        self._file_size = None
        self.pst_blob = None
        self.valid = True

    def _validate(self) -> bool:
        for b in self._client.list_blobs():
            if b.name == self.pst_blob_name:
                self.pst_blob = b
                return True
        return False

    def _get_file(self):
        tmp_file = NamedTemporaryFile(delete=False, prefix="ratom-")
        logger.info(f"Downloading to {tmp_file.name}")
        with Path(tmp_file.name).open(mode="wb") as fh:
            self.blob_data = self._client.download_blob(self.pst_blob)
            self._file_size = self.blob_data.size
            fh.write(self.blob_data.readall())
            self.blob_data = None
            self._data = tmp_file.name

    def open(self):
        self._get_file()
        super().open()
        Path(self._data).unlink()

    @property
    def path(self):
        return self.pst_blob_name

    @property
    def exists(self):
        self._service = BlobServiceClient(
            account_url=self.account_url, credential=settings.AZURE_BLOB_KEY
        )
        self._client = self._service.get_container_client(self.container)
        self.valid = self._validate()
        if not self.valid:
            logger.info(f"{self.pst_blob_name} does not exist")
            return False
        logger.info(f"{self.pst_blob_name} exists")
        return True

    @property
    def file_size(self):
        return self._file_size

    @property
    def file_name(self):
        return self.pst_blob_name
