import logging
from pathlib import Path
from typing import Iterable

import pypff
from libratom.lib.pff import PffArchive


logger = logging.getLogger(__name__)


class PstImporter:
    def __init__(self, path: str):
        self.path = Path(path)
        logger.info(f"PstImporter running on {self.path.name}")
        logger.info(f"Opening archive")
        self.archive = PffArchive(self.path)

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
        logger.info("Traversing archive folders")
        for folder in self.archive.folders():
            if not folder.name:  # skip root node
                continue
            folder_path = self.get_folder_abs_path(folder)
            logger.info(
                f"Scanning {folder.number_of_sub_messages} messages in folder {folder.name}"
            )
            for message in folder.sub_messages:
                logger.debug(f"Message from {message.sender_name}: {message.subject}")


def import_psts(paths: Iterable[str]) -> None:
    for path in paths:
        importer = PstImporter(path)
        importer.run()
