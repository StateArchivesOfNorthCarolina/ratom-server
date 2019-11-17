import datetime as dt
import logging
import re
from pathlib import Path
from typing import Pattern, Union, List

import pypff
import pytz
from libratom.lib.pff import PffArchive
from django.db import transaction
from django.utils.timezone import make_aware

from ratom import models as ratom
from ratom.util.bulk_create_manager import BulkCreateManager


logger = logging.getLogger(__name__)
from_re = re.compile(r"^[fF]rom:\s+(?P<value>.*)$", re.MULTILINE)
to_re = re.compile(r"^[tT]o:\s+(?P<value>.*)$", re.MULTILINE)
title_re = re.compile(r"[a-zA-Z_]+")


class PstImporter:
    def __init__(self, path: str):
        self.path = Path(path)
        logger.info(f"PstImporter running on {self.path.name}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)
        logger.info(f"Loaded {self.archive.message_count} messages in archive")

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
            folder_path = self.get_folder_abs_path(folder)
            for message in folder.sub_messages:
                msg = self._create_message(folder_path, message)
                if msg:
                    bulk_mgr.add(msg)
        bulk_mgr.done()

    def _create_collection(self) -> None:
        self.collection = get_collection(self.path)

    def _extract_match(self, pattern: Pattern[str], haystack: str) -> str:
        match = pattern.search(haystack)
        return match.group(1).strip() if match else ""

    def _create_message(
        self, folder_path: str, message: pypff.message
    ) -> Union[ratom.Message, None]:
        headers = message.transport_headers.strip()
        msg_from = self._extract_match(from_re, headers)
        msg_to = self._extract_match(to_re, headers)
        try:
            sent_date = make_aware(message.delivery_time)
        except pytz.NonExistentTimeError:
            logger.exception("Failed to make datetime aware")
            return None
        return ratom.Message(
            message_id=message,
            sent_date=sent_date,
            msg_to=msg_to,
            msg_from=msg_from,
            msg_subject=message.subject,
            msg_body=self.archive.format_message(message),
            collection=self.collection,
            directory=folder_path,
            processor=ratom.Processor.objects.create(),  # TODO: likely impacts BulkCreateManager
        )


def get_collection(path: Path) -> ratom.Collection:
    title = path.with_suffix("").name
    # attempt to clean title to just be the name
    match = title_re.match(path.name)
    if match:
        title = match.group(0).rstrip("_")
    collection, _ = ratom.Collection.objects.get_or_create(
        title=title, accession_date=dt.date.today()
    )
    return collection


@transaction.atomic
def import_psts(paths: List[str], clean: bool) -> None:
    if clean:
        collection = get_collection(Path(paths[0]))
        logger.warning(f"Deleting {collection.title} collection (if exists)")
        collection.delete()
        ratom.Processor.objects.filter(message=None).delete()
    for path in paths:
        importer = PstImporter(path)
        importer.run()
