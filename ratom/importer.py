import datetime as dt
import json
import logging
import re
from pathlib import Path
from typing import Pattern, Union, List
from email import headerregistry

import pypff
import pytz
from django.db.utils import IntegrityError
from typing import List, Set, Dict, Tuple, Optional, ByteString
from spacy.language import Language
from libratom.lib.entities import load_spacy_model
from libratom.lib.pff import PffArchive
from django.db import transaction
from django.utils.timezone import make_aware

from ratom import models as ratom
from ratom.util.bulk_create_manager import BulkCreateManager


logger = logging.getLogger(__name__)
from_re = re.compile(r"^[fF]rom:\s+(?P<value>.*)$", re.MULTILINE)
to_re = re.compile(r"^[tT]o:\s+(?P<value>.*)$", re.MULTILINE)
title_re = re.compile(r"[a-zA-Z_]+")


def clean_null_chars(obj: str) -> str:
    """Cleans strings of postgres breaking null chars.
    
    Arguments:
        obj {str} 
    
    Returns:
        str
    """
    return re.sub('\x00', "", obj)

class MessageHeader:
    """Provides a consistent interface to the mail and MIME headers from a pypff message.
    """

    def __init__(self, headers: str) -> None:
        self.raw_headers = headers
        self.parsed_headers: Dict[str, str] = {}
        self.decompose_headers()

    def decompose_headers(self) -> None:
        """[summary]
        """
        if self.raw_headers:
            decomp = re.split(r'\r\n', re.sub(r'\r\n\s', '\t', self.raw_headers.strip()))
            for header_item in decomp:
                s = header_item.split(":", 1)
                self.parsed_headers[s[0]] = s[1]
    
    def get_header(self, key: str) -> str:
        return self.parsed_headers.get(key, "")
    
    def get_full_headers(self) -> str:
        return json.dumps(self.parsed_headers)

class PstImporter:
    def __init__(self, path: str, spacy_model: Language):
        self.path = Path(path)
        self.spacy_model = spacy_model
        logger.info(f"PstImporter running on {self.path.name}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)
        logger.info(f"Opened {self.archive.message_count} messages in archive")

    def get_folder_abs_path(self, folder: pypff.folder) -> str:
        """Traverse tree node parent's to build absolute path"""
        path = [folder.name]
        parent = self.archive.tree.get_node(
            self.archive.tree.get_node(folder.identifier).bpointer
        )
        while parent:
            tag = parent.tag if parent.tag != "root" else ""
            path.insert(0, tag)
            parent = self.archive.tree.get_node(
                self.archive.tree.get_node(parent.identifier).bpointer
            )
        return "/".join(path)

    def run(self) -> None:
        self._create_collection()
        logger.info("Traversing archive folders")
        for folder in self.archive.folders():
            if not folder.name:  # skip root node
                continue
            logger.info(
                f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
            )
            if folder.number_of_sub_messages == 0:
                continue

            folder_path = self.get_folder_abs_path(folder)
            for message in folder.sub_messages:
                self._create_message(folder_path, message)

    def _create_collection(self) -> None:
        self.collection = get_collection(self.path)

    def _create_message(
        self, folder_path: str, pypff_message: pypff.message
    ) -> Union[ratom.Message, None]:
        try:
            headers = MessageHeader(pypff_message.transport_headers)
        except AttributeError as e:
            logger.exception(f"{e}")
        msg_from = headers.get_header('from')
        msg_to = headers.get_header('to')
        msg_body = self.archive.format_message(pypff_message, with_headers=False)
        msg_subject = headers.get_header('subject')
        try:
            sent_date = make_aware(pypff_message.delivery_time)
        except pytz.NonExistentTimeError:
            logger.exception("Failed to make datetime aware")
            return None
        # spaCy
        spacy_text = f"{msg_subject}\n{msg_body}"
        try:
            document = self.spacy_model(spacy_text)
        except ValueError:
            logger.exception(f"spaCy error")
            return None
        # spaCy jsonb (idea #1)
        labels = set()
        for entity in document.ents:
            labels.add(entity.label_)

        msg_data = {"labels": list(labels)}
        try:
            ratom_message = ratom.Message.objects.create(
                message_id=pypff_message.identifier,
                sent_date=sent_date,
                msg_to=msg_to,
                msg_from=msg_from,
                msg_subject=msg_subject,
                msg_body=clean_null_chars(msg_body),
                msg_headers=headers.get_full_headers(),
                collection=self.collection,
                directory=folder_path,
                data=msg_data,
            )  # type: ratom.Message
        except IntegrityError as e:
            logger.exception(f"{pypff_message.identifier}: \t {e}")
            return None
        except ValueError as e:
            import pudb; pudb.set_trace()
            logger.exception(f"{pypff_message.identifier}: \t {e}")
            return None
        # # spaCy m2m (idea #2)
        # bulk_mgr = BulkCreateManager(chunk_size=100)
        # for entity in document.ents:
        #     bulk_mgr.add(
        #         ratom.Entity(
        #             label=entity.label_, value=entity.text.strip(), message=ratom_message
        #         )
        #     )
        # bulk_mgr.done()

def get_collection(path: Path) -> ratom.Collection:
    title = path.with_suffix("").name
    # attempt to clean title to just be the name
    match = title_re.match(path.name)
    if match:
        title = match.group(0).rstrip("_")
    collection, _ = ratom.Collection.objects.get_or_create(
        title=title, accession_date=dt.date(2019, 11, 18)
    )
    return collection


def import_psts(paths: List[str], clean: bool) -> None:
    logger.info("Import process started")
    spacy_model_name = "en_core_web_sm"
    logger.info(f"Loading {spacy_model_name} spacy model")
    spacy_model, spacy_model_version = load_spacy_model(spacy_model_name)
    assert spacy_model
    logger.info(
        f"Loaded spacy model: {spacy_model_name}, version: {spacy_model_version}"
    )
    if clean:
        collection = get_collection(Path(paths[0]))
        logger.warning(f"Deleting {collection.title} collection (if exists)")
        collection.delete()
        ratom.Processor.objects.filter(message=None).delete()
    for path in paths:
        importer = PstImporter(path, spacy_model)
        importer.run()
