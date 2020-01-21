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
def archive_msg(empty_message):
    """
    Returns:
        A mock message with fake data
    """
    empty_message.identifier = 2097220
    empty_message.plain_text_body = "Hello, World!"
    headers = [
        "date: Mon, 2 Apr 2001 11:10:00 -0700 (PDT) Mon, 2 Apr 2001 11:10:00 -0700  (PDT)",
        "Message-ID: <PPCBV2QFM1HWPI3I1YTQ5013JUTHIZOCB@zlsvr22>",
        "MIME-Version: 1.0",
        'Content-Type: text/plain; charset="us-ascii"',
        "Content-Transfer-Encoding: 7bit",
        'from: "Lester Rawson"',
        'to: "Kate Symes"',
        "subject: Re: Unit Contingent Deals",
        "filename: kate symes 6-27-02.nsf",
        "folder: \\kate symes 6-27-02\\Notes Folders\\All documents",
    ]
    empty_message.transport_headers = "\r\n".join(headers)
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
