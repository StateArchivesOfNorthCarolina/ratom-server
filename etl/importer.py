import datetime as dt
import io
import json
import logging
import re
from pathlib import Path
from typing import Union
import mimetypes
from hashlib import md5

import pypff
import pytz
from django.db.utils import IntegrityError
from django.conf import settings

from django.core.files.storage import default_storage
from typing import List, Dict
from spacy.language import Language
from libratom.lib.entities import load_spacy_model
from libratom.lib.pff import PffArchive
from django.utils.timezone import make_aware

from core import models as ratom


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
                self.parsed_headers[s[0]] = s[1].lstrip()

    def get_header(self, key: str) -> str:
        return self.parsed_headers.get(key, "")

    def get_full_headers(self) -> str:
        return json.dumps(self.parsed_headers)


class PstImporter:
    def __init__(
        self, path: Path, account: ratom.Account, spacy_model: Language,
    ):
        logger.info(f"PstImporter running on {path}")
        self.local_path = path
        self.account = account
        self.spacy_model = spacy_model
        self.errors = []
        self.data = {}
        self.seen_hashes = []

    def initializing_stage(self) -> None:
        logger.info("Initializing:")
        self.ratom_file = self._create_ratom_file(self.account, self.local_path)
        logger.info(f"Using ratom.File {self.ratom_file.pk}")

    def importing_stage(self) -> None:
        logger.info("Importing:")
        logger.info(f"Opening archive {self.local_path}")
        self.archive = PffArchive(self.local_path)
        self.ratom_file.import_status = ratom.FileImportStatus.IMPORTING
        self.ratom_file.reported_total_messages = self.archive.message_count
        self.ratom_file.save()
        logger.info(f"Opened {self.archive.message_count} messages in archive")

    def _create_ratom_file(self, account: ratom.Account, path: Path) -> ratom.File:
        ratom_file, _ = ratom.File.objects.get_or_create(
            account=account,
            filename=str(path.name),
            original_path=str(path.absolute()),
            file_size=path.stat().st_size,
        )
        return ratom_file

    def import_messages(self) -> None:
        for folder in self.archive.folders():
            if not folder.name:  # skip root node
                continue
            logger.info(
                f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
            )
            if folder.get_number_of_sub_messages() == 0:
                continue
            folder_path = self.get_folder_abs_path(folder)
            for message in folder.sub_messages:  # type: pypff.message
                self._create_message(folder_path, message)

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

    def _save_attachment(self, attachment: pypff.attachment) -> str:
        """Saves the attachment if it does not already exist.
        Attachments are saved using their md5 hexdigest as a name.
        No extension is saved??
        :returns string: the hexdigest of the attachment
        """
        fo = io.BytesIO()
        hasher = md5()
        while True:
            buff = attachment.read_buffer(2048)
            if buff:
                fo.write(buff)
                hasher.update(buff)
                continue
            break
        hex_digest = hasher.hexdigest()
        path = f"{settings.ATTACHMENT_PATH}/{hex_digest}"
        if not default_storage.exists(path):
            default_storage.save(path, fo)
        fo = None
        hasher = None
        return hex_digest

    def run(self) -> None:
        try:
            self.initializing_stage()
            self.importing_stage()
            self.import_messages(data_file)
        except Exception as e:
            self.stage_fail(e)
        else:
            self.stage_success(import_summary)

    def _prepare_message(self, msg_data, archive_msg):
        try:
            headers = MessageHeader(archive_msg.transport_headers)
        except AttributeError as e:
            logger.exception(f"{e}")
            msg_data["errors"].append(e)
        body = self.archive.format_message(archive_msg, with_headers=False)
        sent_date = None
        try:
            sent_date = make_aware(archive_msg.delivery_time)
        except pytz.NonExistentTimeError:
            logger.exception("Failed to make datetime aware")
            msg_data["errors"].append("Failed to make datetime aware")
        except pytz.AmbiguousTimeError:
            logger.exception("Ambiguous Time Could not parse")
            msg_data["errors"].append("Ambiguous time could not parse")
        msg_data.update(
            {
                "msg_from": headers.get_header("From"),
                "msg_to": headers.get_header("To"),
                "msg_cc": headers.get_header("Cc"),
                "msg_bcc": headers.get_header("Bcc"),
                "sent_date": sent_date,
                "subject": headers.get_header("Subject"),
                "headers": headers.get_full_headers(),
                "body": body,
            }
        )

    def _create_message(self, archive_msg: pypff.message, folder_path: str) -> None:
        """create_messages
        Takes a pypff folder and attempts to ingest its messages.

        Any errors are stored in a dict. If a message has errors this dict will be added to the
        msg_data field.

        :param folder: pypff.folder
        :return:
        """
        logger.info(f"Ingesting ({archive_msg.identifier}): {archive_msg.subject}")
        msg_data = {"errors": []}
        self._prepare_message(archive_msg, msg_data)

        spacy_text = f"{subject}\n{body}"
        try:
            document = self.spacy_model(spacy_text)
        except ValueError:
            logger.exception(f"spaCy error")
            msg_data["errors"].append("spaCy Error")

        tags = set()
        for entity in document.ents:
            tag, __ = ratom.Tag.objects.get_or_create(
                type=ratom.TagTypeEnum.IMPORTER, name=entity.label_
            )
            tags.add(tag)

        audit = ratom.MessageAudit.objects.create()
        audit.tags.add(*list(tags))
        tags = None

        try:
            ratom_message = ratom.Message.objects.create(
                source_id=m.identifier,
                file=self.file,
                account=self.file.account,
                audit=audit,
                sent_date=sent_date,
                msg_from=msg_from,
                msg_to=msg_to,
                msg_cc=msg_cc,
                msg_bcc=msg_bcc,
                subject=subject,
                body=clean_null_chars(body),
                directory=folder_path,
                headers=headers.get_full_headers(),
                errors=json.dumps(self.errors),
            )  # type: ratom.Message
        except IntegrityError as e:
            logger.exception(f"{m.identifier}: \t {e}")
        except ValueError as e:
            logger.exception(f"{m.identifier}: \t {e}")
            ratom_message = ratom.Message.objects.create(
                source_id=m.identifier,
                file=self.file,
                account=self.file.account,
                audit=audit,
                msg_from=msg_from,
                msg_to=msg_to,
                msg_cc=msg_cc,
                msg_bcc=msg_bcc,
                subject=subject,
                body=clean_null_chars(body),
                directory=folder_path,
                headers=headers.get_full_headers(),
                errors=json.dumps(self.errors),
            )

        # if ratom_message:
        #     for a in m.attachments:  # type: pypff.attachment
        #         logger.info(f"Storing attachment({a.identifier}): {a.name} - {a.size}")
        #         hashed_name = self._save_attachment(a)
        #         file_name = a.name
        #         if not file_name:
        #             file_name = hashed_name
        #
        #         mime, encoding = mimetypes.guess_type(file_name)
        #         if not mime:
        #             mime = "Unknown"
        #         attachment = api.Attachments.objects.create(
        #             message=ratom_message,
        #             file_name=file_name,
        #             mime_type=mime,
        #             hashed_name=hashed_name,
        #         )


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
    account, created = get_account(account)
    if clean:
        files = get_files(account)
        logger.warning(f"Deleting {account.title} Account (if exists)")
        for f in files.all():
            f.delete()
    for path in paths:
        file, created = create_file(path, account)
        importer = PstImporter(file, spacy_model)
        importer.run()
