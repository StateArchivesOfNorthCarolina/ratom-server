import pytest
from django.urls import reverse

import core.tests.factories as factory
from core.models import User


@pytest.mark.django_db
def test_messages_filter_on_account(client, django_user_model):
    """Test that adding an account query param to the search_messages endpoint filters messages by account."""
    user = factory.UserFactory.create()
    User.objects.create(email=user.email, password=user.password)
    login_response = client.login(email=user.email, password=user.password)
    print(login_response)
    account = factory.AccountFactory.create()
    url = reverse("search_messages")
    client.login()
    response = client.get(url + "?account=" + str(account.id))
    content = response.content.decode()
    print(content)
    # TODO this is using the dev database, not the ratom_test...
