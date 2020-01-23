import factory

from core import models as core


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
