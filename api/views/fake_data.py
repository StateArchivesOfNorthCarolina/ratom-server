from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import Account, MessageAudit

from api.faker.data import load_data

__all__ = ("reset_fake_data",)


ACCOUNT_TITLE_1 = "Bill Rapp [Staging Test Data]"


@api_view(["GET"])
def reset_fake_data(request):
    account, _ = Account.objects.get_or_create(title=ACCOUNT_TITLE_1)
    # Delete all messages associated with fake account
    account.files.all().delete()
    ratom_file1 = account.files.create(
        filename="fake_account1.pst", original_path="/tmp/fake_account1.pst",
    )
    messages = load_data("bill_rapp.json")
    for message in messages:
        message.object.account = account
        message.object.file = ratom_file1
        message.object.audit = MessageAudit.objects.create()
        message.object.save()
    ratom_file1.reported_total_messages = ratom_file1.message_set.count()
    ratom_file1.save()
    return Response("Done")
