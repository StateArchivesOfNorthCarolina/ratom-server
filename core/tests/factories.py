from pathlib import PosixPath
from random import randint

import pytz

import factory

from core import models as core


timezone = pytz.timezone("America/New_York")
path_faker = factory.Faker("file_path", depth=4)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.User

    email = factory.Faker("ascii_email")
    password = "testing"


class MessageAuditFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.MessageAudit


class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.Account

    title = factory.Faker("name")


def fake_paths():
    paths = set()
    for _ in range(0, randint(1, 5)):
        paths.add(str(PosixPath(path_faker.generate()).parent))
    return list(paths)


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.File

    account = factory.SubFactory(AccountFactory)
    filename = factory.Faker("file_name", extension="pst")
    original_path = factory.Faker("file_path", extension="pst")
    sha256 = factory.Faker("text", max_nb_chars=64)
    import_status = core.File.CREATED
    unique_paths = factory.LazyFunction(fake_paths)

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


class LabelFactory(factory.DjangoModelFactory):
    class Meta:
        model = core.Label

    name = factory.Faker("state")
    type = core.Label.IMPORTER
