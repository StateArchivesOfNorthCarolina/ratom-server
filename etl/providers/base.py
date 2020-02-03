from libratom.lib.pff import PffArchive


class ImportProviderError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


class ImportProvider:
    def __init__(self):
        self._data = None
        self.pff_archive = None

    def open(self):
        self.pff_archive = PffArchive(self._data)
        self._data = None

    @property
    def path(self):
        pass

    @property
    def exists(self):
        pass

    @property
    def file_size(self):
        pass
