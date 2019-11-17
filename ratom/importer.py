import datetime as dt
import logging
import re
from pathlib import Path
from typing import Iterable, Pattern

import pypff
from libratom.lib.pff import PffArchive
from django.db import transaction

from ratom import models as ratom
from ratom.util.bulk_create_manager import BulkCreateManager


logger = logging.getLogger(__name__)
from_re = re.compile(r"^[fF]rom:\s+(?P<value>.*)$", re.MULTILINE)
to_re = re.compile(r"^[tT]o:\s+(?P<value>.*)$", re.MULTILINE)


class PstImporter:
    def __init__(self, path: str):
        self.path = Path(path)
        logger.info(f"PstImporter running on {self.path.name}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)
        self.collection = None

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

    @transaction.atomic
    def run(self) -> None:
        self._create_collection()
        logger.info("Traversing archive folders")
        bulk_mgr = BulkCreateManager(chunk_size=100)
        for folder in self.archive.folders():
            if not folder.name:  # skip root node
                continue
            logger.info(
                f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
            )
            for message in folder.sub_messages:
                logger.debug(f"Message from {message.sender_name}: {message.subject}")
                bulk_mgr.add(self._create_message(folder, message))
        bulk_mgr.done()

    def _create_collection(self) -> None:
        collection, _ = ratom.Collection.objects.get_or_create(
            title=self.path.suffix, accession_date=dt.date.today()
        )
        collection.message_set.all().delete()  # TODO: temporary
        self.collection = collection

    def _extract_match(self, pattern: Pattern[str], haystack: str) -> str:
        match = pattern.search(haystack)
        return match.group(1).strip() if match else ""

    def _create_message(
        self, folder: pypff.folder, message: pypff.message
    ) -> ratom.Message:
        headers = message.transport_headers.strip()
        msg_from = self._extract_match(from_re, headers)
        msg_to = self._extract_match(to_re, headers)
        # folder_path = self.get_folder_abs_path(folder)
        return ratom.Message(
            message_id=message,
            sent_date=message.delivery_time,
            msg_to=msg_to,
            msg_from=msg_from,
            msg_subject=message.subject,
            msg_body=self.archive.format_message(message),
            collection=self.collection,
            processor=ratom.Processor(),
        )


def import_psts(paths: Iterable[str]) -> None:
    for path in paths:
        importer = PstImporter(path)
        importer.run()
