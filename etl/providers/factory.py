from etl.providers.base import ImportProvider
from etl.providers.azure import AzureServiceProvider
from etl.providers.filesystem import FilesystemProvider


class ProviderTypes:
    AZURE = 0
    FILESYSTEM = 1


class ImportProviderFactory:
    """
    A factory class that returns a registered provider that implements the ImportProvider
    interface.

    :keyword:
        provider (enum): An class that indicates a type of provider of the factory registry
    """

    def __init__(self):
        self._providers = {}

    def __call__(self, *args, **kwargs) -> ImportProvider:
        return self._providers.get(kwargs["provider"], None)

    def register(self, obj, provider):
        self._providers[obj] = provider


import_provider_factory = ImportProviderFactory()
import_provider_factory.register(ProviderTypes.AZURE, AzureServiceProvider)
import_provider_factory.register(ProviderTypes.FILESYSTEM, FilesystemProvider)
