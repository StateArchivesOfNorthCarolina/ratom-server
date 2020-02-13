import pytest

from core.tests import factories


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
    message.save()
    yield message


@pytest.fixture
def ratom_message_audit(ratom_file):
    message = factories.MessageFactory(account=ratom_file.account, file=ratom_file)
    audit = factories.MessageAuditFactory()
    message.audit = audit
    message.save()
    yield audit
