import os
import time
from pathlib import Path
from typing import List
from zipfile import ZipFile

import pytest
import requests
from requests.exceptions import ChunkedEncodingError, HTTPError

from etl.importer import import_psts
from core import models as ratom

pytestmark = pytest.mark.django_db
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

    Borrowed from: libratom/tests
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
def enron_dataset_bill_rap() -> Path:
    """
    Returns:
        A directory with one PST file:
        bill_rapp_000_1_1.pst
    """

    name = "bill_rapp"
    files = ["bill_rapp_000_1_1.pst"]
    url = f"{ENRON_DATASET_URL}/bill_rapp.zip"

    yield fetch_enron_dataset(name, files, url)


@pytest.mark.skipif(
    os.getenv("TEST_ENRON_DATA_SET", "false") == "false",
    reason="TEST_ENRON_DATA_SET is not set to 'true'",
)
def test_import_enron_dataset_bill_rap(enron_dataset_bill_rap):
    """Run full-stack test against Enron's Bill Rap account."""
    path = enron_dataset_bill_rap / "bill_rapp_000_1_1.pst"
    import_psts([path], "bill_rap", clean=True)
    assert ratom.Account.objects.count() == 1
    assert ratom.File.objects.count() == 1
    bill_rap = ratom.File.objects.get()
    assert bill_rap.message_set.count() == 483
    message = bill_rap.message_set.get(source_id=2097188)
    tags = message.audit.tags.values_list("name", flat=True)
    assert set(tags) == {"CARDINAL", "GPE", "FAC", "ORG", "DATE"}
