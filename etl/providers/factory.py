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


import_provider_factory = ImportProviderFactory()
import_provider_factory.register(ProviderTypes.AZURE.value, AzureServiceProvider)
import_provider_factory.register(ProviderTypes.FILESYSTEM.value, FilesystemProvider)
