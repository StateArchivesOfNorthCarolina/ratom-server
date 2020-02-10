from http import HTTPStatus
import pytest

from django.urls import reverse

from core.models import Account
from api.views.fake_data import ACCOUNT_TITLE

pytestmark = pytest.mark.django_db


def test_reset(api_client_anon):
    response = api_client_anon.post(reverse("reset_fake_data"))
    assert response.status_code == HTTPStatus.OK.value
    account = Account.objects.get(title=ACCOUNT_TITLE)
    assert account.files.count() == 1
