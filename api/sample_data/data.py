from api.sample_data.etl import load_data
from core.models import Account, MessageAudit

SAMPLE_DATA_SETS = (
    {
        "title": "Bill Rapp [Sample Data]",
        "files": ["bill_rapp_sample.pst"],
        "source": "bill_rapp.json",
    },
)


def sample_reset_all():
    """Reset all sample datasets."""
    for dataset in SAMPLE_DATA_SETS:
        reset_dataset(**dataset)


def reset_dataset(title, files, source):
    """Reset specified sample data."""
    account, _ = Account.objects.get_or_create(title=title)
    # Delete all messages associated with fake account
    account.files.all().delete()
    for filename in files:
        ratom_file = account.files.create(
            filename=filename, original_path=f"/tmp/{filename}",
        )
        messages = load_data(source)
        for message in messages:
            message.object.account = account
            message.object.file = ratom_file
            message.object.audit = MessageAudit.objects.create()
            message.object.save()
        ratom_file.reported_total_messages = ratom_file.message_set.count()
        ratom_file.save()
