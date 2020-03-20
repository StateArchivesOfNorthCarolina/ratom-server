from pathlib import Path
from etl.providers.base import ImportProvider
import logging

logger = logging.getLogger(__name__)


class FilesystemProvider(ImportProvider):
    """
    An import provider for RATOM instances that are using a locally available file store.

    :keyword:
       file_path (str) -- a string representing the local path to a file.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.local_path = Path(kwargs.get("file_path", "/"))
        self._data = str(self.local_path.absolute())

    def open(self):
        logger.info(f"Generating cryptographic hash of {self._data}")
        self.hash_file()
        super().open()

    @property
    def path(self):
        return str(self.local_path.absolute())

    @property
    def exists(self):
        return self.local_path.exists()

    @property
    def file_size(self):
        if self.exists:
            return self.local_path.stat().st_size

    @property
    def file_name(self):
        return self.local_path.name
