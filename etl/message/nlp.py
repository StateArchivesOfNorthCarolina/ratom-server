import logging

from core.models import Label


logger = logging.getLogger(__name__)


def extract_labels(text, spacy_model):
    """Extract entities using libratom.

    Returns: core.Label list
    """
    try:
        document = spacy_model(text)
    except ValueError:
        logger.exception(f"spaCy error")
        raise

    labels = set()
    for entity in document.ents:
        label, _ = Label.objects.get_or_create(type=Label.IMPORTER, name=entity.label_)
        labels.add(label)
    return list(labels)
