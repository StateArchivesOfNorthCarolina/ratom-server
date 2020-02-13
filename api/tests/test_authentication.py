from http import HTTPStatus
import pytest

from django.urls import reverse
from django.views.generic.base import View

no_credentials_msg = "Authentication credentials were not provided."
bad_credentials_msg = "Given token not valid for any token type"
http_method_names = set(View.http_method_names) - {"options"}


@pytest.mark.parametrize(
    "url,pk",
    [
        ("user_detail", None),
        ("account_list", None),
        ("search_messages", None),
        ("account_detail", 1),
        ("message_detail", 1),
    ],
)
def test_anonymous_unauthorized(api_client_anon, url, pk):
    kwargs = {"pk": pk} if pk else None
    response = api_client_anon.get(reverse(url, kwargs=kwargs))
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert response.data["detail"] == no_credentials_msg


@pytest.mark.parametrize(
    "url,pk",
    [
        ("user_detail", None),
        ("account_list", None),
        ("search_messages", None),
        ("account_detail", 1),
        ("message_detail", 1),
    ],
)
def test_bad_token(api_client_anon, url, pk):
    api_client_anon.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
    kwargs = {"pk": pk} if pk else None
    response = api_client_anon.get(reverse(url, kwargs=kwargs))
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert response.data["detail"] == bad_credentials_msg


@pytest.mark.parametrize(
    "url,pk,allowed_methods",
    [
        ("user_detail", None, {"get"}),
        ("account_list", None, {"get", "post", "head"}),
        ("account_detail", 1, {"get", "put", "delete"}),
        ("search_messages", None, {"get", "head"}),
        ("message_detail", 1, {"get"}),
    ],
)
@pytest.mark.django_db
def test_get_only_allowed_methods(api_client, url, pk, allowed_methods):
    not_allowed_methods = http_method_names - allowed_methods
    for method in not_allowed_methods:
        client_request = getattr(api_client, method)
        kwargs = {"pk": pk} if pk else None
        response = client_request(reverse(url, kwargs=kwargs))
        assert HTTPStatus.METHOD_NOT_ALLOWED.value == response.status_code, method
