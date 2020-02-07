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
def user(django_db_blocker):
    """ratom.core.models.File instance"""
    with django_db_blocker.unblock():
        yield factories.UserFactory()
