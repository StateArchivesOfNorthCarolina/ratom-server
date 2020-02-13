import pytest


@pytest.mark.django_db
def test_message_audit_update_triggers_message_reindex(
    ratom_message_audit, mock_core_registry
):
    ratom_message_audit.processed = False
    ratom_message_audit.save()
    mock_core_registry.update.assert_called_with(ratom_message_audit.message)
