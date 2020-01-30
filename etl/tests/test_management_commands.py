import pytest
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.fixture(scope="function")
def mock_import_psts():
    with mock.patch("etl.management.commands.import_psts.import_psts") as mock_import:
        yield mock_import


@pytest.fixture(scope="function")
def mock_task_import_psts():
    with mock.patch("etl.tasks.import_psts") as mock_import:
        yield mock_import


def test_missing_path():
    """Command should fail with required positional argument."""
    with pytest.raises(CommandError):
        call_command("import_psts")


def test_import_psts(mock_import_psts, local_file):
    """Test valid values into import_psts()."""
    call_command("import_psts", local_file)
    assert mock_import_psts.called
    assert mock_import_psts.call_args[1]["account"] == local_file.stem
    assert mock_import_psts.call_args[1]["paths"][0] == str(local_file)
    assert not mock_import_psts.call_args[1]["clean"]


def test_import_psts__clean(mock_import_psts, local_file):
    """Clean should be passed through to import_psts()"""
    call_command("import_psts", local_file, clean=True)
    assert mock_import_psts.call_args[1]["clean"]


def test_import_psts__detach(mock_task_import_psts, local_file):
    """Detach should route through task and set is_background=True"""
    call_command("import_psts", local_file, detach=True)
    assert mock_task_import_psts.called
    assert mock_task_import_psts.call_args[1]["is_background"]
