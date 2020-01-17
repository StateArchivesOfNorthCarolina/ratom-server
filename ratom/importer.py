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
    return re.sub("\x00", "", obj)


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
            decomp = re.split(
                r"\r\n", re.sub(r"\r\n\s", "\t", self.raw_headers.strip())
            )
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
            for mps in qs:  # type: ratom.MessageProcessingState
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
                self.folder_path = self.get_folder_abs_path(
                    archive.tree.get_node(folder), archive
                )
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
                ingesting_messages=remaining_ids,
            )

    # def get_folder_abs_path(self, folder: pypff.folder, archive: PffArchive) -> Path:
    #     """Traverse tree node parent's to build absolute path"""
    #     path = [folder.tag]
    #     parent = archive.tree.get_node(
    #         archive.tree.get_node(folder.identifier).bpointer
    #     )
    #     while parent:
    #         tag = parent.tag if parent.tag != "root" else ""
    #         path.insert(0, tag)
    #         parent = archive.tree.get_node(
    #             archive.tree.get_node(parent.identifier).bpointer
    #         )
    #     return Path("/".join(path))

    def keyboard_interrupt_handler(signal: signal, frame: object) -> None:
        logger.fatal("Caught Keyboard interrupt: saving state")
        # save the object


class PstImporter:
    def __init__(self, file: ratom.File, spacy_model: Language) -> None:
        self.file = file
        self.path = file.original_path
        self.spacy_model = spacy_model
        logger.info(f"PstImporter running on {file.filename}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)
        logger.info(f"Opened {self.archive.message_count} messages in archive")
        self.errors = []
        self.data = {}

    def run(self) -> None:
        # for folder in self.archive.folders():
        #     if not folder.name:  # skip root node
        #         continue
        #     logger.info(
        #         f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
        #     )
        #     folder_path = self.get_folder_abs_path(folder)
        self._create_messages()

    def get_folder_abs_path(self, folder: pypff.folder) -> str:
        """Traverse tree node parent's to build absolution path"""
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

    def _create_messages(self) -> None:
        for m in self.archive.messages():
            try:
                headers = MessageHeader(m.transport_headers)
            except AttributeError as e:
                logger.exception(f"{e}")
                self.errors.append(e)
            msg_from = headers.get_header("from")
            msg_to = headers.get_header("to")
            msg_body = self.archive.format_message(m, with_headers=False)
            msg_subject = headers.get_header("subject")
            try:
                sent_date = make_aware(m.delivery_time)
            except pytz.NonExistentTimeError:
                logger.exception("Failed to make datetime aware")
                self.errors.append("Failed to make datetime aware")
            except pytz.AmbiguousTimeError:
                logger.exception("Ambiguous Time Could not parse")
                self.errors.append("Ambiguous time could not parse")
            # spaCy
            spacy_text = f"{msg_subject}\n{msg_body}"
            try:
                document = self.spacy_model(spacy_text)
            except ValueError:
                logger.exception(f"spaCy error")
                self.errors.append("spaCy Error")
            labels = set()
            for entity in document.ents:
                labels.add(entity.label_)

            msg_data = {"labels": list(labels)}
            msg_data["headers"] = headers.raw_headers
            try:
                ratom_message = ratom.Message.objects.create(
                    source_id=m.identifier,
                    file=self.file,
                    account=self.file.account,
                    sent_date=sent_date,
                    msg_to=msg_to,
                    msg_from=msg_from,
                    msg_subject=msg_subject,
                    msg_body=clean_null_chars(msg_body),
                    directory=headers.parsed_headers.get("folder", ""),
                    data=msg_data,
                )  # type: ratom.Message
            except IntegrityError as e:
                logger.exception(f"{m.identifier}: \t {e}")
            except ValueError as e:
                logger.exception(f"{m.identifier}: \t {e}")

            if m.attachments:
                # Store attachments
                print()


def get_account(account: str) -> ratom.Account:
    return ratom.Account.objects.get_or_create(title=account)


def get_files(account: ratom.Account) -> Union[List[ratom.File], List]:
    if account.file_set:
        return account.file_set
    return []


def create_file(path: Path, account: ratom.Account) -> ratom.File:
    return ratom.File.objects.get_or_create(
        account=account,
        filename=str(path.name),
        original_path=str(path.absolute()),
        file_size=path.stat().st_size,
    )


def import_psts(paths: List[Path], account: str, clean: bool) -> None:
    logger.info("Import process started")
    spacy_model_name = "en_core_web_sm"
    logger.info(f"Loading {spacy_model_name} spacy model")
    spacy_model, spacy_model_version = load_spacy_model(spacy_model_name)
    assert spacy_model
    logger.info(
        f"Loaded spacy model: {spacy_model_name}, version: {spacy_model_version}"
    )
    import pudb

    pudb.set_trace()
    account, created = get_account(account)
    if clean:
        files = get_files(account)
        logger.warning(f"Deleting {account.title} Account (if exists)")
        for f in files:
            f.delete()
        account.delete()
    for path in paths:
        file, created = create_file(path, account)
        importer = PstImporter(file, spacy_model)
        importer.run()
