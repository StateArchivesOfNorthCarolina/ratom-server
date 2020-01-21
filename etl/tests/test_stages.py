import pytest

from core import models as ratom

pytestmark = pytest.mark.django_db


def test_create_ratom_file(pst_importer, local_file, account):
    """Importer should create ratom.File with correct initial values."""
    ratom_file = pst_importer._create_ratom_file(account, local_file)
    assert str(local_file.absolute()) == ratom_file.original_path
    assert local_file.name == ratom_file.filename
    assert local_file.stat().st_size == ratom_file.file_size


@pytest.mark.parametrize("message_count", [100, 1_000])
def test_importing_stage_message_count(test_archive, pst_importer, message_count):
    test_archive.return_value.message_count = message_count
    pst_importer.initializing_stage()
    pst_importer.importing_stage()
    assert ratom.File.objects.count() == 1
    ratom_file = pst_importer.ratom_file
    ratom_file.refresh_from_db()
    assert ratom_file.reported_total_messages == message_count
