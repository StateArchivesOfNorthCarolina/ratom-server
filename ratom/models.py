from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_CHOICES = (("ARCHIVIST", "Archivist"), ("RESEARCHER", "Researcher"))
    user_type = models.CharField(max_length=32, choices=USER_CHOICES)


class Collection(models.Model):
    title = models.CharField(max_length=200)
    accession_date = models.DateField(auto_now=False)


class Processor(models.Model):
    processed = models.BooleanField(default=False)
    is_record = models.BooleanField(default=True)
    has_pii = models.BooleanField(default=False)
    date_processed = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )


class Message(models.Model):
    message_id = models.CharField(max_length=256, null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    sent_date = models.CharField(max_length=32)
    msg_from = models.TextField(db_index=True)
    msg_to = models.TextField(db_index=True)
    msg_cc = models.TextField()
    msg_bcc = models.TextField()
    msg_subject = models.TextField(db_index=True)
    msg_body = models.TextField(null=True, blank=True)
    msg_tagged_body = models.TextField()
    processor = models.OneToOneField(
        Processor, on_delete=models.PROTECT, null=True, blank=True
    )
