import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client_anon():
    yield APIClient()


@pytest.fixture
def api_client(api_client_anon, user):
    api_client_anon.force_authenticate(user=user)
    yield api_client_anon
