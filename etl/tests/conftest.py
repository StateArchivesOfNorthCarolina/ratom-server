import pytest
from unittest import mock

from etl.importer import PstImporter


@pytest.fixture()
def local_file(tmp_path):
    """Basic tempfile on filesystem"""
    sub_directory = tmp_path / "sub"
    sub_directory.mkdir()
    pst_file = sub_directory / "name.pst"
    pst_file.write_text("CONTENT")
    yield pst_file


@pytest.fixture()
def pst_importer(account, local_file):
    """PstImporter instance"""
    yield PstImporter(local_file, account, "en_core_web_sm")


@pytest.fixture
def empty_message():
    """
    Returns:
        A mock message with empty components
    """

    message = mock.Mock()
    for attr in ("plain_text_body", "html_body", "rtf_body", "transport_headers"):
        setattr(message, attr, "")

    yield message


@pytest.fixture
def archive_message(empty_message):
    """
    Returns:
        A mock message with fake data
    """
    empty_message.plain_text_body = "Hello, World!"
    yield empty_message


@pytest.fixture
def archive_folder(archive_message):
    """
    Returns:
        A mock pypff folder with messages
    """
    folder = mock.Mock()
    folder.name = "Inbox"
    folder.sub_messages = mock.Mock()
    folder.sub_messages[0] = archive_message
    yield folder


@pytest.fixture()
def test_archive():
    with mock.patch("etl.importer.PffArchive") as _mock:
        archive = _mock.return_value
        archive.message_count = 1
        archive.folders = mock.MagicMock()
        archive.folders[0].name = "Inbox"
        archive.folders[0].sub_messages = mock.MagicMock()
        yield _mock
