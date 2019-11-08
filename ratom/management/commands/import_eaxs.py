from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from django.utils import timezone
from lxml import etree

from ratom.util.bulk_create_manager import BulkCreateManager
from ratom.models import Message, Collection, Processor


class Command(BaseCommand):
    help = 'Takes xml collection and stuffs it in to the db'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        path = options['path'][0]
        eaxs_file = Path(path) / 'ratom/management/commands/test_account.xml'
        message_tag = "Message"
        messages = etree.iterparse(str(eaxs_file.absolute()), events=("end",), strip_cdata=False,
                                   tag=message_tag, huge_tree=True)

        collection, _created = Collection.objects.get_or_create(
            pk=1, title="John Z Ambrose", accession_date=timezone.now())
        collection.save()

        bulk_mgr = BulkCreateManager(chunk_size=100)
        for m in messages:
            processor = Processor.objects.create()
            derived_m = {}
            for element in m[1].iter():
                if element.tag == 'MessageId':
                    derived_m['message_id'] = element.text
                if element.tag == 'OrigDate':
                    derived_m['sent_date'] = element.text
                if element.tag == "From":
                    derived_m['msg_from'] = element.text
                if element.tag == "To":
                    derived_m['msg_to'] = element.text
                if element.tag == "Cc":
                    derived_m['msg_cc'] = element.text
                if element.tag == 'Bcc':
                    derived_m['msg_bcc'] = element.text
                if element.tag == "Subject":
                    derived_m['msg_subject'] = element.text
                if element.tag == "Content":
                    derived_m['msg_body'] = element.text

            derived_m['collection'] = collection
            derived_m['processor'] = processor
            bulk_mgr.add(Message(**derived_m))
        bulk_mgr.done()
