from pathlib import Path

from django.core import serializers
from django.conf import settings

from core.models import Account


def extract_data(account, total):
    """Extract and serialize a subset of messages."""
    account = Account.objects.get(title=account)
    # Explicit ordering so we can attempt to re-generate the same
    # list in the future
    messages = account.messages.order_by("sent_date", "source_id")[:total]
    rows = []
    for message in messages:
        for field in ("account", "file", "audit", "pk"):
            setattr(message, field, None)
        rows.append(message)
    return serializers.serialize("json", rows, indent=2)


def load_data(filename):
    """Load and deserialize saved JSON data."""
    path = Path(settings.PROJECT_ROOT) / "api/sample_data" / filename
    json_data = path.read_text()
    return serializers.deserialize("json", json_data)
