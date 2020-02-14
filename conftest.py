import pytest
from unittest import mock

from core.tests import factories


@pytest.fixture(scope="session", autouse=True)
def mock_es_registry():
    """Fixture to mock ES registry and use it automatically in every test."""
    with mock.patch("django_elasticsearch_dsl.signals.registry") as mock_registry:
        yield mock_registry


@pytest.fixture(scope="session", autouse=True)
def mock_core_registry():
    """Fixture to mock ES registry from core.signals and use it automatically in every test."""
    with mock.patch("core.signals.registry") as mock_core_registry:
        yield mock_core_registry


@pytest.fixture
def account():
    """ratom.core.models.Account instance"""
    yield factories.AccountFactory()


@pytest.fixture
def ratom_file(account):
    """ratom.core.models.File instance"""
    yield factories.FileFactory(account=account)


@pytest.fixture
def file_account(ratom_file):
    """Get a file's account"""
    yield ratom_file.account


@pytest.fixture
def user(django_db_blocker):
    """ratom.core.models.File instance"""
    with django_db_blocker.unblock():
        yield factories.UserFactory()


@pytest.fixture
def ratom_message(ratom_file):
    message = factories.MessageFactory(account=ratom_file.account, file=ratom_file)
    message.audit = factories.MessageAuditFactory()
    yield message


@pytest.fixture
def ratom_message_audit(ratom_file):
    message = factories.MessageFactory(account=ratom_file.account, file=ratom_file)
    audit = factories.MessageAuditFactory()
    message.audit = audit
    yield audit
