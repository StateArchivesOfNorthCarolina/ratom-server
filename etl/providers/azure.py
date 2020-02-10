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
        self.valid = None

    def _setup(self):
        """Establish Azure services and run validations."""
        if not self._client:
            logger.info(f"Initiating Azure service client for {self.account_url}")
            self._service = BlobServiceClient(
                account_url=self.account_url, credential=settings.AZURE_BLOB_KEY
            )
            self._client = self._service.get_container_client(self.container)
        if self.valid is None:
            self.valid = self._validate()

    def _validate(self) -> bool:
        """Obtain blob metadata and set blob state."""
        for b in self._client.list_blobs():
            if b.name == self.pst_blob_name:
                self.pst_blob = b
                self._file_size = self.pst_blob.size
                return True
        return False

    def _get_file(self):
        tmp_file = NamedTemporaryFile(delete=False, prefix="ratom-")
        logger.info(f"Downloading to {tmp_file.name}")
        with Path(tmp_file.name).open(mode="wb") as fh:
            self.blob_data = self._client.download_blob(self.pst_blob)
            fh.write(self.blob_data.readall())
            logger.info("Download complete")
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
        self._setup()
        exists = "does" if self.valid else "does not"
        logger.info(f"{self.pst_blob_name} {exists} exist")
        return self.valid

    @property
    def file_size(self):
        self._setup()
        return self._file_size

    @property
    def file_name(self):
        return self.pst_blob_name
