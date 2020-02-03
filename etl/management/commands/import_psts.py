import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from etl.tasks import import_file_task
from etl.importer import import_psts
from etl.providers.filesystem import FilesystemProvider


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import .pst files"

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="+", type=str)
        parser.add_argument(
            "--clean",
            default=False,
            action="store_true",
            help="Clear collection records before starting import",
        )
        parser.add_argument(
            "--detach",
            default=False,
            action="store_true",
            help="Run task in background",
        )
        parser.add_argument(
            "--account", help="Name of the account for this set of paths"
        )

    def handle(self, *args, **options):
        logger.info("import_psts started")
        paths = [FilesystemProvider(local_path=Path(x)) for x in options["paths"]]
        logger.info(f"Matched {len(paths)} file(s)")
        data = {
            "paths": paths,
            "account": options["account"],
            "clean": options["clean"],
        }
        if options["detach"]:
            logger.info("Queuing background task...")
            import_file_task.delay(**data)
        else:
            import_psts(**data)
