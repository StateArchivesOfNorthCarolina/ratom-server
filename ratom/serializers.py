from rest_framework import serializers

from .models import User, Account, Message

from .documents.message import MessageDocument


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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "title", "accession_date"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "message_id",
            "sent_date",
            "msg_from",
            "msg_to",
            "subject",
            "headers",
            "body",
            "directory",
            "data",
        ]


class MessageDocumentSerializer(serializers.Serializer):
    """Serializer for the Message document."""

    id = serializers.IntegerField(read_only=True)
    message_id = serializers.CharField(read_only=True)
    sent_date = serializers.DateTimeField(read_only=True)
    msg_from = serializers.CharField(read_only=True)
    msg_to = serializers.CharField(read_only=True)
    subject = serializers.CharField(read_only=True)
    headers = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
    directory = serializers.CharField(read_only=True)
    labels = serializers.SerializerMethodField()

    def get_labels(self, obj):
        """Get labels."""
        if obj.labels:
            return list(obj.labels)
        else:
            return []

    # account = serializers...

    class Meta(object):
        document = MessageDocument

        fields = (
            "id",
            "message_id",
            # "account",
            "sent_date",
            "msg_from",
            "msg_to",
            "subject",
            "headers",
            "body",
            "directory",
            "labels",
        )
