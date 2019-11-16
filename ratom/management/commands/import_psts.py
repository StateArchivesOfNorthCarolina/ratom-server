from django.core.management.base import BaseCommand

from ratom.importer import import_psts


class Command(BaseCommand):
    help = "Import .pst files"

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="+", type=str)

    def handle(self, *args, **options):
        import_psts(options["paths"])
