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
def container_client(pst_blob):
    client = mock.Mock()
    client.primary_endpoint = "https://blob.windows.net"
    client.list_blobs.return_value = [pst_blob]
    yield client


@pytest.fixture
def cloud_provider(pst_blob, container_client):
    Provider = import_provider_factory(provider=ProviderTypes.AZURE)
    provider = Provider(file_path="inbox.pst")
    provider._client = container_client
    provider._service = mock.Mock()
    yield provider


def test_azure_file_name():
    Provider = import_provider_factory(provider=ProviderTypes.AZURE)
    provider = Provider(file_path="inbox.pst")
    assert provider.file_name == "inbox.pst"


def test_azure_path(cloud_provider, container_client):
    container_client.primary_endpoint = "https://ratom.com"
    assert container_client.primary_endpoint in cloud_provider.path


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


def test_azure_blob__open(cloud_provider, tmp_path):
    with mock.patch("etl.providers.base.PffArchive") as archive_mock:
        pst_file = tmp_path / "name.pst"
        pst_file.write_bytes(b"Binary file contents")
        cloud_provider._client.download_blob = mock.Mock()
        cloud_provider._client.download_blob.return_value.readall.return_value = (
            pst_file.read_bytes()
        )
        cloud_provider.open()
        assert archive_mock.called_once
