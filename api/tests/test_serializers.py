import datetime as dt
from django.utils import timezone
import pytest

import factory
from api.serializers import MessageAuditSerializer
from core.models import Label

pytestmark = pytest.mark.django_db


def test_serializer_expected_fields(ratom_message_audit):
    serializer = MessageAuditSerializer(instance=ratom_message_audit)
    assert set(serializer.data.keys()) == {
        "id",
        "processed",
        "is_record",
        "date_processed",
        "is_restricted",
        "labels",
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
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert getattr(instance, field)


def test_always_processed(ratom_message_audit, user):
    """Any interaction with serializer will mark it as processed with a date."""
    ratom_message_audit.processed = False
    ratom_message_audit.date_processed = None
    ratom_message_audit.save()
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={})
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert instance.processed
    assert instance.date_processed


def test_updated_by(ratom_message_audit, user):
    """User is supplied in save() method"""
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={})
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert instance.updated_by == user


@pytest.mark.parametrize(
    "field,val",
    [
        ("is_record", True),
        ("is_record", False),
        ("is_restricted", True),
        ("is_restricted", False),
        ("needs_redaction", True),
        ("needs_redaction", False),
    ],
)
def test_audit_flag_values(ratom_message_audit, user, field, val):
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={field: val})
    assert serializer.is_valid(), serializer.errors
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


def test_valid_restricted_until(ratom_message_audit, user):
    """Make sure restricted_until date sets properly."""
    date = dt.datetime.now()
    serializer = MessageAuditSerializer(
        instance=ratom_message_audit, data={"restricted_until": date.isoformat()}
    )
    assert serializer.is_valid(), serializer.errors
    aware_date = timezone.make_aware(date)
    assert serializer.validated_data["restricted_until"] == aware_date
    instance = serializer.save(updated_by=user)
    assert instance.restricted_until == aware_date


@pytest.mark.parametrize(
    "field,val",
    [
        ("is_record", True),
        ("is_record", False),
        ("restricted_until", timezone.now()),
        ("is_restricted", True),
        ("is_restricted", False),
        ("needs_redaction", True),
        ("needs_redaction", False),
    ],
)
def test_partial_updates_do_not_reset_omitted_fields(
    ratom_message_audit, user, field, val
):
    """If only certian fields are supplied, make sure omitted fields are not reset to defaults."""
    setattr(ratom_message_audit, field, val)
    ratom_message_audit.save()
    serializer = MessageAuditSerializer(instance=ratom_message_audit, data={})
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert getattr(instance, field) == val


def test_audit_append_user_label__new(ratom_message_audit, user):
    name = "new"
    serializer = MessageAuditSerializer(
        instance=ratom_message_audit, data={"append_user_label": name}
    )
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert instance.labels.filter(type=Label.USER, name=name).exists()


def test_audit_append_user_label__existing(ratom_message_audit, user, user_label):
    serializer = MessageAuditSerializer(
        instance=ratom_message_audit, data={"append_user_label": user_label.name}
    )
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert instance.labels.filter(type=Label.USER, name=user_label.name).exists()
    assert Label.objects.count() == 1  # still only should be one label


def test_add_label_does_not_process_record(ratom_message_audit, user, user_label):
    """
    A bug existed that caused records to be marked as "Open Record" on the front end
    after adding a label. Adding labels should not mark a record as "processed".
    """
    assert ratom_message_audit.processed is False
    serializer = MessageAuditSerializer(
        instance=ratom_message_audit, data={"append_user_label": user_label.name}
    )
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    # After updating a label, processed should remain False
    assert instance.processed is False


def test_audit_append_user_label__case_insensitive_existing(
    ratom_message_audit, user, user_label
):
    ratom_message_audit.labels.add(user_label)
    serializer = MessageAuditSerializer(
        instance=ratom_message_audit,
        data={"append_user_label": user_label.name.upper()},
    )
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save(updated_by=user)
    assert instance.labels.count() == 1
    assert Label.objects.count() == 1  # still only should be one label


def test_bulk_audit_update(ratom_message_audit, ratom_message_audit_2, user):
    audits = [ratom_message_audit, ratom_message_audit_2]
    effect_args = {
        "is_record": False,
        "is_restricted": False,
        "needs_redaction": False,
    }
    data = [{"id": a.pk, **effect_args} for a in audits]
    serializer = MessageAuditSerializer(
        data=data, instance=audits, many=True, partial=True
    )
    assert serializer.is_valid(), serializer.errors
    serializer.save(updated_by=user)
    for audit in audits:
        assert not audit.is_record
        assert not audit.is_restricted
        assert not audit.needs_redaction
