import datetime as dt
import json
import logging
import re
from pathlib import Path
from typing import Pattern, Union, List
from email import headerregistry
from collections import deque
import signal

import pypff
import pytz
from django.db.utils import IntegrityError
from typing import List, Set, Dict, Tuple, Optional, ByteString
from spacy.language import Language
from libratom.lib.entities import load_spacy_model
from libratom.lib.pff import PffArchive
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import make_aware

from ratom import models as ratom
from ratom.util.bulk_create_manager import BulkCreateManager
from msg_parser import MsOxMessage


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


class MessageManager:
    def __init__(self, account_id: int) -> None:
        self.account_id = account_id
        self.folder_path: Union[str, None] = None
        self.folder_id: Union[int, None] = None
        self.folder_ids: deque[int] = deque()
        self.message_ids: deque[int] = deque()
        self.failed_ids: deque[int] = deque()
        self.account_map: Dict[int, deque[int]] = {}
        self.current_folder: Union[int, None] = None
        self.current_messages: Union[deque[int], None] = None
        self._set_in_process_map()

    def add_failed_id(self, msg_id: int):
        if msg_id not in self.failed_ids:
            self.failed_ids.append(msg_id)

    def _set_in_process_map(self) -> None:
        qs = ratom.MessageProcessingState.objects.filter(account=self.account_id)
        if qs:
            for mps in qs:   # type: ratom.MessageProcessingState
                self.account_map[mps.ingesting_folder] = mps.ingesting_messages

    def build_map(self, folder: pypff.folder):
        self.current_folder = folder.identifier
        self.current_messages = deque()
        for message in folder.sub_messages:  # type: pypff.message
            self.current_messages.append(message.identifier)
        self.account_map[self.current_folder] = self.current_messages
        self.current_messages = deque()
        self.current_folder = None

    def process_messages_for_account(self, archive: PffArchive) -> pypff.message:
        try:
            for folder, messages in self.account_map.items():
                self.folder_path = self.get_folder_abs_path(archive.tree.get_node(folder), archive)
                self.current_folder = folder
                while True:
                    try:
                        mess = messages.popleft()
                        mess = archive.tree.get_node(mess)
                        yield mess.data
                    except IndexError:
                        break
                self.account_map[folder] = messages
        except Exception as e:
            pass
        finally:
            self.save_state()

    def save_state(self):
        remaining_ids = self.failed_ids + self.current_messages
        if remaining_ids:
            ratom.MessageProcessingState.update_or_create(
                account=self.account_id,
                ingesting_folder=self.current_folder,
                ingesting_messages=remaining_ids
            )

    def get_folder_abs_path(self, folder: pypff.folder, archive: PffArchive) -> Path:
        """Traverse tree node parent's to build absolute path"""
        path = [folder.tag]
        parent = archive.tree.get_node(
            archive.tree.get_node(folder.identifier).bpointer
        )
        while parent:
            tag = parent.tag if parent.tag != "root" else ""
            path.insert(0, tag)
            parent = archive.tree.get_node(
                archive.tree.get_node(parent.identifier).bpointer
            )
        return Path("/".join(path))

    def keyboard_interrupt_handler(signal: signal, frame: object) -> None:
        logger.fatal("Caught Keyboard interrupt: saving state")
        # save the object


class PstImporter:
    
    def __init__(self, path: str, spacy_model: Language) -> None:
        self.path = Path(path)
        self.spacy_model = spacy_model
        logger.info(f"PstImporter running on {self.path.name}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)
        logger.info(f"Opened {self.archive.message_count} messages in archive")

    def run(self) -> None:
        self._create_collection()
        # import pudb; pudb.set_trace()
        message_manager = MessageManager(self.collection)
        if not message_manager.account_map:
            logger.info("Traversing archive folders")
            for folder in self.archive.folders():  # type: pypff.folder
                if not folder.name:  # skip root node
                    continue
                logger.info(
                    f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
                )
                if folder.number_of_sub_messages == 0:
                    continue
                message_manager.build_map(folder)
        self._create_messages(message_manager)

    def _create_collection(self) -> None:
        self.collection = get_collection(self.path)

    def _create_messages(self, message_manager: MessageManager) -> None:
        for m in message_manager.process_messages_for_account(self.archive):
            try:
                headers = MessageHeader(m.transport_headers)
            except AttributeError as e:
                logger.exception(f"{e}")
                message_manager.add_failed_id(m.id)
            msg_from = headers.get_header('from')
            msg_to = headers.get_header('to')
            msg_body = self.archive.format_message(m, with_headers=False)
            msg_subject = headers.get_header('subject')
            try:
                sent_date = make_aware(m.delivery_time)
            except pytz.NonExistentTimeError:
                logger.exception("Failed to make datetime aware")
                message_manager.add_failed_id(m.id)
            except pytz.AmbiguousTimeError:
                logger.exception("Ambiguous Time Could not parse")
                message_manager.add_failed_id(m.id)
            # spaCy
            spacy_text = f"{msg_subject}\n{msg_body}"
            try:
                document = self.spacy_model(spacy_text)
            except ValueError:
                logger.exception(f"spaCy error")
                message_manager.add_failed_id(m.id)
            # spaCy jsonb (idea #1)
            labels = set()
            for entity in document.ents:
                labels.add(entity.label_)

            msg_data = {"labels": list(labels)}
            try:
                ratom_message = ratom.Message.objects.create(
                    message_id=m.identifier,
                    sent_date=sent_date,
                    msg_to=msg_to,
                    msg_from=msg_from,
                    msg_subject=msg_subject,
                    msg_body=clean_null_chars(msg_body),
                    msg_headers=headers.get_full_headers(),
                    collection=self.collection,
                    directory=str(message_manager.folder_path),
                    data=msg_data,
                )  # type: ratom.Message
            except IntegrityError as e:
                logger.exception(f"{m.identifier}: \t {e}")
                message_manager.add_failed_id(m.id)
            except ValueError as e:
                logger.exception(f"{m.identifier}: \t {e}")
                message_manager.add_failed_id(m.id)



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
