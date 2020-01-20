import factory

from ratom import models as ratom


class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = ratom.Account

    title = factory.Faker("name")


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = ratom.File

    account = factory.SubFactory(AccountFactory)
    filename = factory.Faker("file_name", extension="pst")
    original_path = factory.Faker("file_path", extension="pst")
    md5_hash = factory.Faker("md5")
    import_status = ratom.FileImportStatus.CREATED
