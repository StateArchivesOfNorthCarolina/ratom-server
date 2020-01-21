from django import forms

from core.models import Message


class ArchiveMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        pass

    class Meta:
        model = Message
