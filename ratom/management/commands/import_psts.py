from django.core.management.base import BaseCommand

from ratom.importer import import_psts


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

    def handle(self, *args, **options):
        import_psts(paths=options["paths"], clean=options["clean"])
