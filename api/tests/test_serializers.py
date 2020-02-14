import pytest

import factory
from api.serializers import MessageAuditSerializer


pytestmark = pytest.mark.django_db


def test_serializer_expected_fields(ratom_message_audit):
    serializer = MessageAuditSerializer(instance=ratom_message_audit)
    assert set(serializer.data.keys()) == {
        "processed",
        "is_record",
        "date_processed",
        "is_restricted",
        "needs_redaction",
        "restricted_until",
        "updated_by",
    }


@pytest.mark.parametrize(
    "field,val", [("processed", False), ("date_processed", None), ("updated_by", None),]
)
def test_ignore_read_only_fields(ratom_message_audit, user, field, val):
    """Read-only field and should be ignored."""
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={field: val})
    assert serializer.is_valid()
    instance = serializer.save(updated_by=user)
    assert getattr(instance, field)


def test_always_processed(ratom_message_audit, user):
    """Any interaction with serializer will mark it as processed with a date."""
    ratom_message_audit.processed = False
    ratom_message_audit.date_processed = None
    ratom_message_audit.save()
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={})
    assert serializer.is_valid()
    instance = serializer.save(updated_by=user)
    assert instance.processed
    assert instance.date_processed


def test_updated_by(ratom_message_audit, user):
    """User is supplied in save() method"""
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={})
    assert serializer.is_valid()
    instance = serializer.save(updated_by=user)
    assert instance.updated_by == user


@pytest.mark.parametrize(
    "field,val",
    [
        ("is_record", True),
        ("is_record", False),
        ("is_record", None),
        ("is_restricted", True),
        ("is_restricted", False),
        ("needs_redaction", True),
        ("needs_redaction", False),
    ],
)
def test_audit_flag_values(ratom_message_audit, user, field, val):
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={field: val})
    assert serializer.is_valid()
    assert field in serializer.validated_data
    instance = serializer.save(updated_by=user)
    assert getattr(instance, field) == val


@pytest.mark.parametrize(
    "field,faker_key",
    [
        ("is_record", "paragraph"),
        ("restricted_until", "paragraph"),
        ("is_restricted", "paragraph"),
        ("needs_redaction", "paragraph"),
    ],
)
def test_bad_values(field, faker_key):
    data = {field: factory.Faker(faker_key)}
    serializer = MessageAuditSerializer(data=data)
    assert not serializer.is_valid()
    assert field in serializer.errors
