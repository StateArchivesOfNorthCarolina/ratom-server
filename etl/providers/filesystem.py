from pathlib import Path
from etl.providers.base import ImportProvider


class FilesystemProvider(ImportProvider):
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
        return self.local_path.stat().st_size

    @property
    def file_name(self):
        return self.local_path.name
