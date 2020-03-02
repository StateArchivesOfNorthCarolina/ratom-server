import logging

from api.sample_data.etl import load_data
from core.models import Account, MessageAudit, File
from etl.message.nlp import extract_labels, load_nlp_model

SAMPLE_DATA_SETS = (
    {
        "title": "Bill Rapp [Sample Data]",
        "files": ["bill_rapp_sample.pst"],
        "source": "bill_rapp.json",
    },
    {
        "title": "Albert Meyers [Sample Data]",
        "files": ["albert_meyers_sample.pst"],
        "source": "albert_meyers.json",
    },
)
logger = logging.getLogger(__name__)


def sample_reset_all():
    """Reset all sample datasets."""
    spacy_model = load_nlp_model()
    for dataset in SAMPLE_DATA_SETS:
        reset_dataset(**dataset, spacy_model=spacy_model)


def reset_dataset(title, files, source, spacy_model):
    """Reset specified sample data."""
    logger.info(f"Resetting sample dataset: {title}")
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
            labels = extract_labels(
                f"{message.object.subject}\n{message.object.body}", spacy_model
            )
            message.object.audit = MessageAudit.objects.create()
            message.object.audit.labels.add(*labels)
            message.object.save()
        ratom_file.reported_total_messages = ratom_file.message_set.count()
        ratom_file.import_status = File.COMPLETE
        ratom_file.save()
