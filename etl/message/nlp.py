import logging

from libratom.lib.entities import load_spacy_model

from core.models import Label


logger = logging.getLogger(__name__)


def load_nlp_model(model_name="en_core_web_sm"):
    logger.info(f"Loading {model_name} spacy model")
    spacy_model, spacy_model_version = load_spacy_model(model_name)
    logger.info(f"Loaded spacy model: {model_name}, version: {spacy_model_version}")
    return spacy_model


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
