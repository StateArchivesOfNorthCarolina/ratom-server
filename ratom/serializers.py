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
        fields = ["id", "title"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "source_id",
            "sent_date",
            "msg_from",
            "msg_to",
            "msg_subject",
            "msg_body",
            "directory",
            "data",
        ]


class MessageDocumentSerializer(serializers.Serializer):
    """Serializer for the Message document."""

    id = serializers.IntegerField(read_only=True)
    source_id = serializers.CharField(read_only=True)
    sent_date = serializers.DateTimeField(read_only=True)
    msg_from = serializers.CharField(read_only=True)
    msg_to = serializers.CharField(read_only=True)
    msg_subject = serializers.CharField(read_only=True)
    msg_body = serializers.CharField(read_only=True)
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
            "source_id",
            # "account",
            "sent_date",
            "msg_from",
            "msg_to",
            "msg_subject",
            "msg_body",
            "directory",
            "labels",
        )
