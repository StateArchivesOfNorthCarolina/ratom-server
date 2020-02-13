import pytest
from unittest import mock
from rest_framework.test import APIClient


@pytest.fixture
def api_client_anon():
    yield APIClient()


@pytest.fixture
def api_client(api_client_anon, user):
    api_client_anon.force_authenticate(user=user)
    yield api_client_anon


@pytest.fixture
def celery_mock():
    with mock.patch("api.views.account.import_file_task") as _mock:
        yield _mock
