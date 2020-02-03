from etl.providers.base import ImportProvider


class FilesystemProvider(ImportProvider):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.local_path = kwargs.get("local_path", None)  # type: 'pathlib.Path'
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
