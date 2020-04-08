import logging
from hashlib import sha256

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

ADDITIONAL_FILE_FOR_ACCOUNT = (
    {
        "title": "Bill Rapp [Sample Data]",
        "files": ["albert_meyers_sample_in_bm.pst"],
        "source": "albert_meyers.json",
    },
)


def ingest_files(account, spacy_model, files, source):
    for filename in files:
        di = sha256()
        di.update(filename.encode("utf-8"))
        ratom_file = account.files.create(
            filename=filename, original_path=f"/tmp/{filename}", sha256=di.hexdigest()
        )
        messages = load_data(source)
        for message in messages:
            message.object.account = account
            message.object.file = ratom_file
            ratom_file.unique_paths.append(message.object.directory)
            labels = extract_labels(
                f"{message.object.subject}\n{message.object.body}", spacy_model
            )
            message.object.audit = MessageAudit.objects.create()
            message.object.audit.labels.add(*labels)
            message.object.save()
        ratom_file.reported_total_messages = ratom_file.message_set.count()
        ratom_file.import_status = File.COMPLETE
        ratom_file.save()


def sample_reset_all():
    """Reset all sample datasets."""
    spacy_model = load_nlp_model()
    for dataset in SAMPLE_DATA_SETS:
        reset_dataset(**dataset, spacy_model=spacy_model)


def sample_add_additional():
    spacy_model = load_nlp_model()
    for dataset in ADDITIONAL_FILE_FOR_ACCOUNT:
        add_dataset(**dataset, spacy_model=spacy_model)


def add_dataset(title, spacy_model, **dataset):
    logger.info(f"Adding new file to: {title}")
    account, created = Account.objects.get_or_create(title=title)
    if created:
        logger.info(f"The account {title} does not exist. Try reset_sample_data first.")
        return
    ingest_files(account=account, spacy_model=spacy_model, **dataset)


def reset_dataset(title, spacy_model, **dataset):
    """Reset specified sample data."""
    logger.info(f"Resetting sample dataset: {title}")
    account, _ = Account.objects.get_or_create(title=title)
    # Delete all messages associated with fake account
    account.files.all().delete()
    ingest_files(account=account, spacy_model=spacy_model, **dataset)
