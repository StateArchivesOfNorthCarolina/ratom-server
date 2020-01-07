from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from elasticsearch_dsl import Index

from ratom.managers import MessageManager
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    USER_CHOICES = (("ARCHIVIST", "Archivist"), ("RESEARCHER", "Researcher"))
    user_type = models.CharField(max_length=32, choices=USER_CHOICES)


class Account(models.Model):
    title = models.CharField(max_length=200)
    collection_name = models.CharField(max_length=512)
    date_of_first_message = models.DateField(null=True)
    date_of_last_message = models.DateField(null=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return str(self.title)


class File(models.Model):
    filename = models.CharField(max_length=256, null=False)
    accession_date = models.DateField(auto_now=False)
    total_messages = models.IntegerField(null=True)
    messages_processed = models.IntegerField(default=0)
    date_of_first_message = models.DateField(null=True)
    date_of_last_message = models.DateField(null=True)
    axaem_id = models.IntegerField(null=True)
    history = HistoricalRecords()

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

class MessageProcessingState(models.Model):
    account = models.ForeignKey(Collection, null=False, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=512, blank=True)
    ingesting_folder = models.IntegerField(null=False)
    ingesting_messages = ArrayField(models.IntegerField(), null=True)

    class Meta:
        unique_together = ['account', 'ingesting_folder']

    def __str__(self) -> str:
        return f"folder_id: {self.ingesting_folder}({len(self.ingesting_messages)})"
