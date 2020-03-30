import pytest
from django.urls import reverse
from core.models import File, Account
from etl.tasks import remove_file_task
from unittest import mock

pytestmark = pytest.mark.django_db


@pytest.fixture
def celery_mock():
    with mock.patch("api.views.file.remove_file_task") as _mock:
        yield _mock


def test_remove_file(ratom_file, api_client, celery_mock):
    ratom_file.import_status = File.FAILED
    ratom_file.save()
    url = reverse("remove_file")
    response = api_client.delete(url, data={"id": ratom_file.account.pk})
    assert response.status_code == 204
    celery_mock.delay.assert_called_once_with([ratom_file.pk])


def test_remove_multiple_files(multiple_file_account, api_client, celery_mock):
    account = multiple_file_account[0].account.id
    failed_ids = []
    for f in multiple_file_account[:2]:
        f.import_status = File.FAILED
        f.save()
        failed_ids.append(f.id)
    url = reverse("remove_file")
    response = api_client.delete(url, data={"id": account})
    assert response.status_code == 204
    failed_ids.reverse()
    celery_mock.delay.assert_called_once_with(failed_ids)


def test_account_removed_if_all_files_removed(multiple_file_account):
    account = multiple_file_account[0].account.id
    failed_ids = []
    for f in multiple_file_account:
        f.import_status = File.FAILED
        f.save()
        failed_ids.append(f.id)
    remove_file_task(failed_ids)
    assert Account.objects.filter(pk=account).count() == 0


def test_file_remove_file_fail(ratom_file, api_client):
    # When no file has a FAILED status
    ratom_file.import_status = File.IMPORTING
    ratom_file.save()
    url = reverse("remove_file")
    response = api_client.delete(url, data={"id": ratom_file.account.pk})
    assert response.status_code == 404


def test_file_remove_file_fail_no_account_id(ratom_file, api_client):
    ratom_file.import_status = File.IMPORTING
    ratom_file.save()
    url = reverse("remove_file")
    # Should also return 404 if there is no account id
    response = api_client.delete(url, data={"id": 600})
    assert response.status_code == 404
