from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import JSONField
from django.db import models
from elasticsearch_dsl import Index

from ratom.managers import MessageManager


class User(AbstractUser):
    USER_CHOICES = (("ARCHIVIST", "Archivist"), ("RESEARCHER", "Researcher"))
    user_type = models.CharField(max_length=32, choices=USER_CHOICES)


class Collection(models.Model):
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
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    processor = models.OneToOneField(
        Processor, on_delete=models.PROTECT, null=True, blank=True
    )
    sent_date = models.DateTimeField()
    msg_from = models.TextField()
    msg_to = models.TextField()
    msg_cc = models.TextField(blank=True)
    msg_bcc = models.TextField(blank=True)
    msg_subject = models.TextField()
    msg_headers = models.TextField(blank=True)
    msg_body = models.TextField(blank=True)
    msg_tagged_body = models.TextField(blank=True)
    directory = models.TextField(blank=True)
    data = JSONField(null=True, blank=True)
    """
    data = JSONField(null=True, blank=True)
    # this seems to crash when using a simple model based query, as such:
    class MessageType(DjangoObjectType):
    class Meta:
        model = Message
    """

    # objects = MessageManager()

    # class Meta:
    #     indexes = [GinIndex(fields=["data"])]


class Entity(models.Model):

    message = models.ForeignKey(
        Message, related_name="entities", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=128)
    value = models.TextField()

    class Meta:
        verbose_name_plural = "Entities"
        # indexes = [models.Index(fields=["label", "value"])]

    def __str__(self) -> str:
        return f"{self.label}: {self.value}"
