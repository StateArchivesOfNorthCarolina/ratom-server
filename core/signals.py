from django.db.models.signals import post_save
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from core.models import MessageAudit


@receiver(post_save)
def update_document(sender, **kwargs):
    """
    Update MessageDocument index if related `message.audit` changes.
    """
    instance = kwargs["instance"]
    if isinstance(instance, MessageAudit):
        print("=======================> Hopefully updating message document index!")
        registry.update(instance.message)
