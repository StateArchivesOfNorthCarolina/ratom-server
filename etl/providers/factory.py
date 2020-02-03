from enum import Enum
from etl.providers.azure import AzureServiceProvider
from etl.providers.filesystem import FilesystemProvider


class ProviderTypes(Enum):
    AZURE = "AZURE"
    FILESYSTEM = "FILESYSTEM"


class ImportProviderFactory:
    def __init__(self):
        self._providers = {}

    def __call__(self, *args, **kwargs):
        return self._providers.get(kwargs["provider"], None)

    def register(self, obj, provider):
        self._providers[obj] = provider


factory = ImportProviderFactory()
factory.register(ProviderTypes.AZURE.value, AzureServiceProvider)
factory.register(ProviderTypes.FILESYSTEM.value, FilesystemProvider)
