import pytest
from django.urls import reverse
from core.models import File
from unittest import mock

pytestmark = pytest.mark.django_db


@pytest.fixture
def celery_mock():
    with mock.patch("api.views.file.import_file_task") as _mock:
        yield _mock


def test_file_restart_file_ingest(ratom_file, api_client, celery_mock):
    ratom_file.import_status = File.FAILED
    ratom_file.save()
    url = reverse("restart_file")
    response = api_client.post(url, data={"id": ratom_file.account.pk})
    assert response.status_code == 204
    celery_mock.delay.assert_called_once_with(
        [ratom_file.filename], ratom_file.account.title, clean_file=True
    )


def test_file_restart_file_ingest_fail(ratom_file, api_client):
    # When no file has a FAILED status
    ratom_file.import_status = File.IMPORTING
    ratom_file.save()
    url = reverse("restart_file")
    response = api_client.post(url, data={"id": ratom_file.account.pk})
    assert response.status_code == 404
    # Should also return 404 if there is no account id
    response = api_client.post(url, data={"id": 600})
    assert response.status_code == 404
