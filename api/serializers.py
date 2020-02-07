import re
from rest_framework import serializers
from core.models import User, Account, Message, File

from api.documents.message import MessageDocument


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "user_type",
        ]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File

    def to_representation(self, instance: File):
        return {
            "filename": instance.filename,
            "original_path": instance.original_path,
            "reported_total_messages": instance.reported_total_messages,
            "accession_date": instance.accession_date,
            "file_size": instance.file_size,
            "md5_hash": instance.md5_hash,
            "import_status": instance.get_import_status_display(),
            "date_imported": instance.date_imported.strftime("%Y-%d-%m, %H:%M:%S"),
        }


class AccountSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Account

    def to_representation(self, instance: Account):

        return {
            "id": instance.id,
            "title": instance.title,
            "files_in_account": instance.files.count(),
            "messages_in_account": instance.total_messages_in_account,
            "processed_messages": instance.total_processed_messages,
            "account_last_modified": instance.account_last_modified.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "inclusive_dates": instance.get_inclusive_dates(
                "%Y-%m-%d", as_string=False
            ),
            "account_status": instance.get_account_status(),
        }


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "source_id",
            "sent_date",
            "msg_from",
            "msg_to",
            "subject",
            "body",
            "directory",
        ]


class MessageHighlightsSerializer(serializers.ModelSerializer):
    highlighted_subject = serializers.SerializerMethodField()
    highlighted_body = serializers.SerializerMethodField()

    def _highlight(self, text):
        highlights_str = self.context.get("highlights")
        highlights = highlights_str.split(",")
        highlighted_text = text
        for highlight in highlights:
            for m in re.finditer(highlight, text, re.IGNORECASE):
                og_text = m.group(0)
                highlighted = "<strong>" + og_text + "</strong>"
                highlighted_text = re.sub(og_text, highlighted, highlighted_text)
        return highlighted_text

    def get_highlighted_subject(self, message):
        if message.subject:
            return self._highlight(message.subject)
        else:
            return None

    def get_highlighted_body(self, message):
        if message.body:
            return self._highlight(message.body)
        else:
            return None

    class Meta:
        model = Message
        fields = [
            "id",
            "source_id",
            "sent_date",
            "msg_from",
            "msg_to",
            "highlighted_subject",
            "highlighted_body",
            "directory",
        ]


class MessageDocumentSerializer(serializers.Serializer):
    """Serializer for the Message document."""

    id = serializers.IntegerField(read_only=True)
    source_id = serializers.CharField(read_only=True)
    sent_date = serializers.DateTimeField(read_only=True)
    msg_from = serializers.CharField(read_only=True)
    msg_to = serializers.CharField(read_only=True)
    subject = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
    directory = serializers.CharField(read_only=True)
    labels = serializers.SerializerMethodField()
    highlight = serializers.SerializerMethodField()

    def get_labels(self, obj):
        """Get labels."""
        if obj.labels:
            return list(obj.labels)
        else:
            return []

    def get_highlight(self, obj):
        if hasattr(obj.meta, "highlight"):
            return obj.meta.highlight.__dict__["_d_"]
        return {}

    class Meta(object):
        document = MessageDocument
        fields = (
            "id",
            "source_id",
            "sent_date",
            "msg_from",
            "msg_to",
            "subject",
            "body",
            "directory",
            "labels",
            "highlight",
        )
