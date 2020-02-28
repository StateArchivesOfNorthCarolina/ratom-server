import pytest

from django.urls import reverse

from core.tests import factories


@pytest.fixture
def url():
    return reverse("search_messages")


@pytest.fixture
def account_eric():
    return factories.AccountFactory()


@pytest.fixture
def account_sally():
    return factories.AccountFactory()


@pytest.fixture
def file_eric(account_eric):
    return factories.FileFactory(account=account_eric)


@pytest.fixture
def file_sally(account_sally):
    return factories.FileFactory(account=account_sally)


@pytest.fixture
def eric1(file_eric):
    return factories.MessageFactory(account=file_eric.account, file=file_eric)


@pytest.fixture
def sally1(file_sally):
    return factories.MessageFactory(account=file_sally.account, file=file_sally)


@pytest.fixture
def sally2(file_sally):
    return factories.MessageFactory(account=file_sally.account, file=file_sally)


@pytest.fixture
def event():
    return factories.LabelFactory(name="EVENT")


@pytest.fixture
def org():
    return factories.LabelFactory(name="ORG")
