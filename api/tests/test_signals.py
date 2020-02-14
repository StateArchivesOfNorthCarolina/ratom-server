import pytest
from core.tests import factories


@pytest.mark.django_db
def test_message_audit_update_triggers_message_reindex(
    ratom_message_audit, mock_core_registry
):
    ratom_message_audit.processed = False
    ratom_message_audit.save()
    mock_core_registry.update.assert_called_with(ratom_message_audit.message)


@pytest.mark.django_db
def test_audit_created_no_signal(mock_core_registry):
    """Verify new audits don't trigger an index update (since message will already do it)."""
    factories.MessageAuditFactory()
    mock_core_registry.update.assert_not_called()
