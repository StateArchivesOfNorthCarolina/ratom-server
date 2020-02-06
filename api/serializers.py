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
    score = serializers.SerializerMethodField()

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

    def get_score(self, obj):
        return obj.meta.score

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
