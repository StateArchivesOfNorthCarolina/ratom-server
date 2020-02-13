import pytest
from unittest import mock


@pytest.mark.django_db
def test_message_audit_update_triggers_message_reindex(ratom_message_audit):
    ratom_message_audit.processed = False
    with mock.patch("core.signals.registry.update") as mock_registry_update:
        ratom_message_audit.save()
        mock_registry_update.assert_called_with(ratom_message_audit.message)
