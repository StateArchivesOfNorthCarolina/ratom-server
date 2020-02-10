import pytest
from unittest import mock

from etl.providers.factory import import_provider_factory, ProviderTypes


@pytest.fixture
def pst_blob():
    blob = mock.Mock()
    blob.name = "inbox.pst"
    blob.size = 100
    yield blob


@pytest.fixture
def cloud_provider(pst_blob):
    Provider = import_provider_factory(provider=ProviderTypes.AZURE)
    provider = Provider(file_path="inbox.pst")
    provider._service = mock.Mock()
    provider._client = mock.Mock()
    provider._client.list_blobs.return_value = [pst_blob]
    yield provider


def test_azure_file_name():
    Provider = import_provider_factory(provider=ProviderTypes.AZURE)
    provider = Provider(file_path="inbox.pst")
    assert provider.file_name == "inbox.pst"


def test_azure_blob__exists(cloud_provider, pst_blob):
    pst_blob.name = "inbox.pst"
    assert cloud_provider.exists


def test_azure_blob__not_exists(cloud_provider, pst_blob):
    pst_blob.name = "i-dont-exist.pst"
    assert not cloud_provider.exists


def test_azure_blob__size_exists(cloud_provider, pst_blob):
    file_size = 1024
    pst_blob.size = file_size
    assert cloud_provider.file_size == file_size


def test_azure_blob__size_not_exists(cloud_provider, pst_blob):
    pst_blob.name = "i-dont-exist.pst"
    assert not cloud_provider.file_size
