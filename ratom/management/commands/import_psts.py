from pathlib import Path
from django.core.management.base import BaseCommand

from ratom.importer import import_psts


class Command(BaseCommand):
    help = "Import .pst files"

    def add_arguments(self: Command, parser: CommandParser) -> None:
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

    def handle(self: Command, *args: list, **options: dict) -> None:
        if options["recursive"]:
            for p in Path(options["paths"][0]).glob("**/*.pst"):
                import_psts(paths=[p.absolute()], clean=options["clean"])
        else:
            import_psts(paths=options["paths"], clean=options["clean"])
