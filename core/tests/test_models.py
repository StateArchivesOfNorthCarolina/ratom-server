import random
from django.test import TestCase
from faker import Faker
from rest_framework.test import APITestCase, APIRequestFactory

import core.tests.factories as factory
import core.models as m

fake = Faker()


class TestUser(APITestCase):
    """
    Test custom user model.
    """

    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.user = {"email": fake.email(), "password": fake.password()}

    def test_user_can_be_created_with_email(self):
        user = m.User.objects.create(**self.user)
        self.assertEqual(user.email, self.user["email"])
        self.assertEqual(user.password, self.user["password"])

    def test_username_is_none(self):
        user = m.User.objects.create(**self.user)
        self.assertEqual(m.User.username, None)
        self.assertEqual(user.username, None)


def generate_messages(account: m.Account, file: m.File) -> [m.Message]:
    messages = []
    for i in range(random.randrange(1, 10)):
        ma = m.MessageAudit.objects.create()
        message = factory.MessageFactory(account=account, file=file)
        message.audit = ma
        message.save()
        messages.append(message)
    return messages


def generate_files(account: m.Account):
    files = []
    for i in range(random.randrange(1, 3)):
        file = factory.FileFactory(account=account)
        files.append(file)
    return files


class TestAccount(TestCase):
    def setUp(self) -> None:
        self.account = factory.AccountFactory()
        self.files = generate_files(account=self.account)
        self.message_map = {}
        for file in self.files:
            messages = generate_messages(account=self.account, file=file)
            file.reported_total_messages = len(messages)
            self.message_map[file] = len(messages)
            file.save()

    def test_relationships(self):
        self.assertEqual(self.account.__str__(), self.files[0].account.title)

    def test_messages_in_account(self):
        total_messages = 0
        for k, v in self.message_map.items():
            total_messages += v
        self.assertEqual(self.account.total_messages_in_account, total_messages)

    def test_processed_messages(self):
        """Nothing processed 0 messages processed"""
        self.assertEqual(self.account.total_processed_messages, 0)

        with self.subTest("2 processed messages"):
            should_have = 1
            if m.Message.objects.all().count() > 1:
                should_have = 2
                messages = m.Message.objects.all()[0:2]
                for mes in messages:
                    mes.audit.is_record = False
                    mes.audit.processed = True
                    mes.audit.save()
            self.assertEqual(self.account.total_processed_messages, should_have)

    def test_account_dates(self):
        files = m.File.objects.all()
        f = files[files.count() - 1]
        self.assertEqual(self.account.account_last_modified, f.date_imported)

        with self.subTest("Test inclusive dates"):
            messages = m.Message.objects.all()
            first = messages[0].sent_date
            last = messages[messages.count() - 1].sent_date

            account_dates = self.account.get_inclusive_dates(as_string=False)
            self.assertEqual(first, account_dates[0])
            self.assertEqual(last, account_dates[1])

            # Test stringyfied
            string_dates = self.account.get_inclusive_dates()
            self.assertEqual(first.strftime(m.YMD_HMS), string_dates[0])
            self.assertEqual(last.strftime(m.YMD_HMS), string_dates[1])

            # Test custom format
            string_dates = self.account.get_inclusive_dates(str_fmt="%d")
            self.assertEqual(first.strftime("%d"), string_dates[0])
            self.assertEqual(last.strftime("%d"), string_dates[1])

    def test_account_import_status(self):
        files = m.File.objects.all()
        with self.subTest("All are Complete"):
            for f in files:
                f.import_status = m.File.COMPLETE
                f.save()
            self.assertEqual(self.account.get_account_status(), m.File.COMPLETE)

        with self.subTest("One is importing"):
            files[0].import_status = m.File.IMPORTING
            files[0].save()
            self.assertEqual(self.account.get_account_status(), m.File.IMPORTING)

        with self.subTest("One is Failed"):
            files[0].import_status = m.File.FAILED
            files[0].save()
            self.assertEqual(self.account.get_account_status(), m.File.FAILED)
