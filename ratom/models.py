from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from elasticsearch_dsl import Index
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj

from ratom.managers import MessageManager


class User(AbstractUser):
    USER_CHOICES = (("ARCHIVIST", "Archivist"), ("RESEARCHER", "Researcher"))
    user_type = models.CharField(max_length=32, choices=USER_CHOICES)


class Account(models.Model):
    title = models.CharField(max_length=200)
    accession_date = models.DateField(auto_now=False)

    def __str__(self) -> str:
        return str(self.title)


class Processor(models.Model):
    processed = models.BooleanField(default=False)
    is_record = models.BooleanField(default=True)
    has_pii = models.BooleanField(default=False)
    date_processed = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(null=True)
    last_modified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )


class Message(models.Model):
    message_id = models.CharField(max_length=256, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    sent_date = models.DateTimeField()
    msg_from = models.TextField()
    msg_to = models.TextField()
    subject = models.TextField()
    headers = models.TextField(blank=True)
    body = models.TextField(blank=True)
    directory = models.TextField(blank=True)
    data = JSONField(null=True, blank=True)

    @property
    def account_indexing(self):
        """Account data (nested) for indexing.

        Example:
        >>> mapping = {
        >>>     "account": {
        >>>         "title": "Gov Purdue"
        >>>     }
        >>> }

        :return:
        """
        return dict_to_obj({"title": self.account.title,})

    @property
    def labels_indexing(self):
        labels = []
        if self.data:
            labels = list(self.data.get("labels", []))
        return labels
