import pytest

from core.tests import factories


@pytest.fixture
def account():
    """ratom.core.models.Account instance"""
    return factories.AccountFactory()


@pytest.fixture
def ratom_file(account):
    """ratom.core.models.File instance"""
    return factories.FileFactory(account=account)
