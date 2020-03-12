from django.core.management.base import BaseCommand

from api.sample_data.data import sample_add_additional


class Command(BaseCommand):
    help = "Reset sample data"

    def handle(self, *args, **options):
        sample_add_additional()
