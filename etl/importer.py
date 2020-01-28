import logging
from pathlib import Path
from typing import List

from libratom.lib.entities import load_spacy_model
from libratom.lib.pff import PffArchive
from spacy.language import Language
from tqdm import tqdm
import pypff

from core import models as ratom
from etl.message.forms import ArchiveMessageForm
from etl.message.nlp import extract_labels


logger = logging.getLogger(__name__)


class PstImporter:
    def __init__(
        self,
        path: Path,
        account: ratom.Account,
        spacy_model: Language,
        is_background: bool,
    ):
        logger.info(f"PstImporter running on {path}")
        self.local_path = path
        self.account = account
        self.spacy_model = spacy_model
        self.is_background = is_background
        self.ratom_file_errors = []

    def initializing_stage(self) -> None:
        """Initialization step prior to starting import process."""
        logger.info("--- Initializing Stage ---")
        self.ratom_file = self._create_ratom_file(self.account, self.local_path)
        logger.info(f"Using ratom.File[{self.ratom_file.pk}]")

    def importing_stage(self) -> None:
        """Set import_status to IMPORTING and open PffArchive."""
        logger.info("--- Importing Stage ---")
        logger.info(f"Opening archive {self.local_path}")
        self.archive = PffArchive(self.local_path)
        self.ratom_file.import_status = ratom.File.IMPORTING
        self.ratom_file.reported_total_messages = self.archive.message_count
        self.ratom_file.save()
        logger.info(f"Opened {self.archive.message_count} messages in archive")

    def fail_stage(self, e) -> None:
        """Import failed for some reason, set import_status to FAILED."""
        logger.info("--- Fail Stage ---")
        self.ratom_file.import_status = ratom.File.FAILED
        self.ratom_file.errors = self.ratom_file_errors
        self.ratom_file.save()
        logger.info(f"ratom.File[{self.ratom_file.pk}] failed to import")

    def success_stage(self) -> None:
        """If import was successful, set import_status to COMPLETE."""
        logger.info("--- Success Stage ---")
        self.ratom_file.import_status = ratom.File.COMPLETE
        self.ratom_file.save()
        logger.info(f"ratom.File[{self.ratom_file.pk}] imported successfully")

    def _create_ratom_file(self, account: ratom.Account, path: Path) -> ratom.File:
        """Create ratom.File for provided Account.

        Returns: ratom.File instance
        """
        ratom_file, _ = ratom.File.objects.get_or_create(
            account=account,
            filename=str(path.name),
            original_path=str(path.absolute()),
            file_size=path.stat().st_size,
        )
        return ratom_file

    def import_messages_from_archive(self) -> None:
        """Loop through and import all archive messages."""
        for folder in self.archive.folders():
            if not folder.name:  # skip root node
                continue
            message_count = folder.get_number_of_sub_messages()
            logger.info(f"Scanning {message_count} messages in folder {folder.name}")
            if message_count == 0:
                continue
            folder_path = self.get_folder_abs_path(folder)
            msg_iterator = tqdm(
                folder.sub_messages,
                unit="msgs",
                initial=0,
                total=message_count,
                miniters=message_count * 0.05 if self.is_background else 1,
            )
            for archive_msg in msg_iterator:  # type: pypff.message
                try:
                    self.create_message(folder_path, archive_msg)
                except Exception as e:
                    name = "create_message() failed"
                    logger.exception(name)
                    self.add_file_error(
                        name=name, context=str(e), archive_msg=archive_msg
                    )

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
        """Validate message, run NLP, and create ratom.Message instance.

        Any errors are stored in a dict. If a message has errors this dict will be added to the
        msg_data field.
        """
        logger.debug(f"Ingesting ({archive_msg.identifier}): {archive_msg.subject}")
        form = ArchiveMessageForm(archive=self.archive, archive_msg=archive_msg)
        if not form.is_valid():
            # A discovered error will prevent saving this message
            # so log the error and move on to next message
            logger.error(form.errors)
            self.add_file_error(
                name="ArchiveMessageForm not valid",
                context=form.errors,
                archive=archive_msg,
            )
            return

        ratom_message = form.save(commit=False)
        # perform spaCy NLP and entity extraction
        labels = extract_labels(
            f"{ratom_message.subject}\n{ratom_message.body}", self.spacy_model
        )
        ratom_message.audit = ratom.MessageAudit.objects.create()
        ratom_message.audit.labels.add(*list(labels))
        # lastly, save instance
        ratom_message.file = self.ratom_file
        ratom_message.account = self.ratom_file.account
        ratom_message.directory = folder_path
        ratom_message.errors = form.msg_errors
        ratom_message.save()

    def add_file_error(self, name, context, archive_msg=None):
        """Record file-level error occured."""
        error_data = {"name": name, "context": context}
        if archive_msg:
            error_data["msg_identifier"] = archive_msg.identifier
        self.ratom_file_errors.append(error_data)

    def run(self) -> None:
        """Main staged import process."""
        try:
            self.initializing_stage()
            self.importing_stage()
            self.import_messages_from_archive()
        except KeyboardInterrupt as e:
            name = "Keyboard interrupted file import process"
            logger.warning("Keyboard interrupted file import process")
            self.add_file_error(name=name, context=str(e))
            self.fail_stage(e)
        except Exception as e:
            name = "Unrecoverable import error"
            logger.exception(name)
            self.add_file_error(name=name, context=str(e))
            self.fail_stage(e)
        else:
            self.success_stage()


def import_psts(
    paths: List[str], account: str, clean: bool, is_background: bool
) -> None:
    logger.info("Import process started")
    spacy_model_name = "en_core_web_sm"
    logger.info(f"Loading {spacy_model_name} spacy model")
    spacy_model, spacy_model_version = load_spacy_model(spacy_model_name)
    assert spacy_model
    logger.info(
        f"Loaded spacy model: {spacy_model_name}, version: {spacy_model_version}"
    )
    account, _ = ratom.Account.objects.get_or_create(title=account)
    if clean:
        logger.warning(f"Deleting {account.title} account files (if exists)")
        account.file_set.all().delete()
    for path in paths:
        importer = PstImporter(Path(path), account, spacy_model, is_background)
        importer.run()
