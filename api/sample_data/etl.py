import datetime as dt
from pathlib import Path

from django.core import serializers
from django.conf import settings
from django.utils.timezone import make_aware

from core.models import Account


def extract_data(account, total):
    """Extract and serialize a subset of messages."""
    account = Account.objects.get(title=account)
    # Explicit ordering so we can attempt to re-generate the same
    # list in the future. Here we grab the first message of each
    # week to limit chances of seeing duplicated messages within
    # the same email thread.
    rows = []
    for idx, date in enumerate(account.messages.dates("sent_date", "week")):
        if idx == total:
            break
        start = make_aware(dt.datetime(date.year, date.month, date.day))
        message = (
            account.messages.filter(sent_date__gt=start).order_by("sent_date").first()
        )
        for field in ("account", "file", "audit", "pk"):
            setattr(message, field, None)
        rows.append(message)
    return serializers.serialize("json", rows, indent=2)


def load_data(filename):
    """Load and deserialize saved JSON data."""
    path = Path(settings.PROJECT_ROOT) / "api/sample_data" / filename
    json_data = path.read_text()
    return serializers.deserialize("json", json_data)
