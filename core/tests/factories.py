import factory
from core import models as core
import pytz

timezone = pytz.timezone("America/New_York")


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.User


class MessageAuditFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.MessageAudit


class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.Account

    title = factory.Faker("name")


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.File

    account = factory.SubFactory(AccountFactory)
    filename = factory.Faker("file_name", extension="pst")
    original_path = factory.Faker("file_path", extension="pst")
    md5_hash = factory.Faker("md5")
    import_status = core.File.CREATED

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        if kwargs.get("account"):
            obj.account = kwargs["account"]
        obj.save()
        return obj


class MessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.Message

    account = factory.SubFactory(AccountFactory)
    audit = factory.SubFactory(MessageAuditFactory)
    source_id = factory.Faker("random_int")
    file = factory.SubFactory(FileFactory)
    sent_date = factory.Faker("date_time", tzinfo=timezone)
    msg_to = factory.Faker("ascii_email")
    msg_from = factory.Faker("ascii_email")
    msg_cc = factory.Faker("ascii_email")
    subject = factory.Faker("text", max_nb_chars=64)
    body = factory.Faker("paragraph", nb_sentences=5)
    directory = "/TestUser/Inbox"
    headers = {
        "Sent: ": f"{sent_date}\n",
        "From: ": f"{msg_from}\n",
        "To: ": f"{msg_to}\n",
        "Subject: ": f"{subject}\n\n",
    }

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        if kwargs.get("account"):
            obj.account = kwargs["account"]
        if kwargs.get("file"):
            obj.file = kwargs["file"]
        obj.save()
        return obj
