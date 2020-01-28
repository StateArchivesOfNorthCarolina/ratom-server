from pathlib import Path
from django.core.management.base import BaseCommand
from etl.tasks import import_file_task
from etl.importer import import_psts


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
            "--recursive",
            default=False,
            action="store_true",
            help="Find and import all psts in a structure",
        )
        parser.add_argument(
            "--detach",
            default=False,
            action="store_true",
            help="Run task in background",
        )

    def handle(self, *args, **options):
        for p in Path(options["paths"][0]).glob("**/*.pst"):
            if options["detach"]:
                import_file_task.delay(
                    path=[str(p)], account=p.stem, clean=options["clean"]
                )
            else:
                import_psts(paths=[str(p)], account=p.stem, clean=options["clean"])
