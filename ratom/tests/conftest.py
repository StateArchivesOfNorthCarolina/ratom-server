from unittest import mock

import pytest

from ratom.tests import factories

from ratom.importer import PstImporter

import requests
from typing import List
from pathlib import Path
from requests.exceptions import ChunkedEncodingError, HTTPError

from zipfile import ZipFile

ENRON_DATASET_URL = "https://www.ibiblio.org/enron/RevisedEDRMv1_Complete"
CACHED_ENRON_DATA_DIR = Path("/tmp/libratom/test_data/RevisedEDRMv1_Complete")
CACHED_HTTPD_USERS_MAIL_DIR = Path("/tmp/libratom/test_data/httpd-users")


def fetch_enron_dataset(name: str, files: List[str], url: str) -> Path:
    """Downloads and caches a given part of the Enron dataset archive (one per individual)
    Args:
        name: The individual's name
        files: A list of expected PST files
        url: The download URL for that file
    Returns:
        A directory path
    """
    path = CACHED_ENRON_DATA_DIR / name

    if not path.exists():
        # Make the directories
        CACHED_ENRON_DATA_DIR.mkdir(parents=True, exist_ok=True)
        zipped_path = CACHED_ENRON_DATA_DIR / f"{name}.zip"

        # Fetch the zipped PST file
        max_tries = 5
        for i in range(1, max_tries + 1):
            try:
                response = requests.get(url, timeout=(6.05, 30))

                if response.ok:
                    zipped_path.write_bytes(response.content)
                else:
                    response.raise_for_status()

                # success
                break

            except (ChunkedEncodingError, HTTPError):
                if i < max_tries:
                    time.sleep(i)
                else:
                    raise

        # Unzip and remove archive
        ZipFile(zipped_path).extractall(path=CACHED_ENRON_DATA_DIR)
        zipped_path.unlink()

    # Confirm the files are there
    for filename in files:
        assert (path / filename).is_file()

    return path


@pytest.fixture(scope="session")
def enron_dataset_part001() -> Path:
    """
    Returns:
        A directory with one PST file:
        albert_meyers_000_1_1.pst
    """

    name = "albert_meyers"
    files = ["albert_meyers_000_1_1.pst"]
    url = f"{ENRON_DATASET_URL}/albert_meyers.zip"

    yield fetch_enron_dataset(name, files, url)


@pytest.fixture()
def test_archive():
    with mock.patch("ratom.importer.PffArchive") as _mock:
        archive = _mock.return_value
        archive.message_count = 1
        archive.folders = mock.MagicMock()
        archive.folders[0].name = "Inbox"
        archive.folders[0].sub_messages = mock.MagicMock()

        # archive.folders[1].name = "Sent Mail"
        # archive.folders[0].sub_messages = mock.MagicMock()
        yield _mock


@pytest.fixture()
def account():
    return factories.AccountFactory()


@pytest.fixture()
def ratom_file(account):
    return factories.FileFactory(account=account)


@pytest.fixture()
def local_file(tmp_path):
    sub_directory = tmp_path / "sub"
    sub_directory.mkdir()
    pst_file = sub_directory / "name.pst"
    pst_file.write_text("CONTENT")
    yield pst_file


@pytest.fixture()
def pst_importer(account, local_file):
    yield PstImporter(local_file, account, "en_core_web_sm")


@pytest.fixture
def empty_message(mocker):
    """
    Returns:
        A mock message with empty components
    """

    message = mocker.Mock()
    for attr in ("plain_text_body", "html_body", "rtf_body", "transport_headers"):
        setattr(message, attr, "")

    yield message


@pytest.fixture
def archive_message(mocker, empty_message):
    empty_message.plain_text_body = "Hello, World!"
    yield empty_message


@pytest.fixture
def archive_folder(mocker, archive_message):
    folder = mocker.Mock()
    folder.name = "Inbox"
    folder.sub_messages = mocker.Mock()
    folder.sub_messages[0] = archive_message
    yield folder
