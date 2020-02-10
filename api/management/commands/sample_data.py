from django.core.management.base import BaseCommand

from api.sample_data.etl import extract_data


class Command(BaseCommand):
    help = "Extract fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--account", help="Name of account to pull data from", required=True,
        )
        parser.add_argument(
            "--total", help="Total rows to extract", default=10,
        )

    def handle(self, *args, **options):
        print(extract_data(account=options["account"], total=options["total"]))
