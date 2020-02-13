import pytest
from unittest import mock


@pytest.mark.django_db
def test_message_audit_update_triggers_message_reindex(ratom_message_audit):
    ratom_message_audit.processed = False
    with mock.patch("core.signals.registry") as mock_registry:
        ratom_message_audit.save()
        mock_registry.update.assert_called_once_with(ratom_message_audit.message)
