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

    @property
    def path(self):
        return str(self.local_path.absolute())

    @property
    def exists(self):
        return self.local_path.exists()

    @property
    def file_size(self):
        try:
            return self.local_path.stat().st_size
        except FileNotFoundError:
            logger.info(f"{self.file_name} not found. Filesize set to 0")
            return 0

    @property
    def file_name(self):
        return self.local_path.name
