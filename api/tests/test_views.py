import pytest
from django.urls import reverse
from core.models import File


def test_user_detail(api_client):
    url = reverse("user_detail")
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_detail_view(ratom_file, api_client):
    account = ratom_file.account
    url = reverse("account_detail", args=[account.pk])
    response = api_client.get(url)
    assert response.status_code == 200

    # Test No account exists
    url = reverse("account_detail", args=[5000])
    response = api_client.get(url)
    assert response.status_code == 404

    # Figure out how to test PUT

    # Test Delete account
    url = reverse("account_detail", args=[account.pk])
    response = api_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_account_list_view(ratom_file, api_client):
    account = ratom_file.account
    url = reverse("account_list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data[0]["title"] == account.title
    assert response.data[0]["files_in_account"] == 1
    assert response.data[0]["account_status"] == File.CREATED
