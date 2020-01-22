import logging
import re
from pathlib import Path
from typing import List, Union

from libratom.lib.entities import load_spacy_model
from libratom.lib.pff import PffArchive
from spacy.language import Language
import pypff

from core import models as ratom
from etl.message.forms import ArchiveMessageForm
from etl.message.nlp import extract_tags


logger = logging.getLogger(__name__)
from_re = re.compile(r"^[fF]rom:\s+(?P<value>.*)$", re.MULTILINE)
to_re = re.compile(r"^[tT]o:\s+(?P<value>.*)$", re.MULTILINE)
title_re = re.compile(r"[a-zA-Z_]+")


class PstImporter:
    def __init__(
        self, path: Path, account: ratom.Account, spacy_model: Language,
    ):
        logger.info(f"PstImporter running on {path}")
        self.local_path = path
        self.account = account
        self.spacy_model = spacy_model

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

    def import_messages_from_archive(self) -> None:
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
                self.create_message(folder_path, message)

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

    def create_message(self, folder_path: str, archive_msg: pypff.message) -> None:
        """create_messages
        Takes a pypff folder and attempts to ingest its messages.

        Any errors are stored in a dict. If a message has errors this dict will be added to the
        msg_data field.

        :param folder: pypff.folder
        :return:
        """
        logger.info(f"Ingesting ({archive_msg.identifier}): {archive_msg.subject}")
        form = ArchiveMessageForm(archive=self.archive, archive_msg=archive_msg)
        if not form.is_valid():
            # A discovered error will prevent saving this message
            # so log the error and move on
            logger.error(form.errors)
            return

        ratom_message = form.save(commit=False)
        # perform spaCy NLP and entity extraction
        tags = extract_tags(
            f"{ratom_message.subject}\n{ratom_message.body}", self.spacy_model
        )
        ratom_message.audit = ratom.MessageAudit.objects.create()
        ratom_message.audit.tags.add(*list(tags))
        # lastly, save instance
        ratom_message.file = self.ratom_file
        ratom_message.account = self.ratom_file.account
        ratom_message.directory = folder_path
        # ratom_message.errors = {}
        ratom_message.save()

    def run(self) -> None:
        try:
            self.initializing_stage()
            self.importing_stage()
            self.import_messages_from_archive()
        except Exception as e:
            self.stage_fail(e)
        else:
            self.stage_success()


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
        # file, created = create_file(path, account)
        importer = PstImporter(path, account, spacy_model)
        importer.run()
