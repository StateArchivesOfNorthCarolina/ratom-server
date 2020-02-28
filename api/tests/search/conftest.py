import pytest

from django.urls import reverse

from core.tests import factories


@pytest.fixture
def url():
    yield reverse("search_messages")


@pytest.fixture
def account_eric():
    yield factories.AccountFactory()


@pytest.fixture
def account_sally():
    yield factories.AccountFactory()


@pytest.fixture
def file_eric(account_eric):
    yield factories.FileFactory(account=account_eric)


@pytest.fixture
def file_sally(account_sally):
    yield factories.FileFactory(account=account_sally)


@pytest.fixture
def message_eric1(file_eric):
    yield factories.MessageFactory(account=file_eric.account, file=file_eric)


@pytest.fixture
def message_sally1(file_eric):
    yield factories.MessageFactory(account=file_sally.account, file=file_sally)


@pytest.fixture
def message_sally2(file_eric):
    yield factories.MessageFactory(account=file_sally.account, file=file_sally)
