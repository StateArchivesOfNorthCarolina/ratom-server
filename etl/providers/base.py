from hashlib import sha256
from pathlib import Path
import logging

from libratom.lib.pff import PffArchive

logger = logging.getLogger(__name__)


class ImportProviderError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


class ImportProvider:
    """Base class that provides an interface to the etl.importer.PstImporter"""

    def __init__(self) -> None:
        self._data = None
        self.pff_archive = None  # type: PffArchive
        self.crypt_hash = None  # type: str

    def open(self) -> None:
        logger.info(f"Opening archive {self._data} with provider")
        self.pff_archive = PffArchive(self._data)

    def hash_file(self):
        with Path(self._data).open(mode="rb") as fh:
            di = sha256()
            while True:
                b = fh.read(10 ** 6)
                if b:
                    di.update(b)
                    continue
                break
            self.crypt_hash = di.hexdigest()

    @property
    def path(self):
        pass

    @property
    def exists(self):
        pass

    @property
    def file_size(self):
        pass

    @property
    def file_name(self):
        pass
