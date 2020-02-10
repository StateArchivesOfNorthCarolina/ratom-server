from http import HTTPStatus
import pytest

from django.urls import reverse

from core.models import Account
from api.sample_data.data import SAMPLE_DATA_SETS

pytestmark = pytest.mark.django_db


def test_reset(api_client_anon):
    response = api_client_anon.get(reverse("reset_sample_data"))
    assert response.status_code == HTTPStatus.OK.value
    account = Account.objects.get(title=SAMPLE_DATA_SETS[0]["title"])
    assert account.files.count() == 1
