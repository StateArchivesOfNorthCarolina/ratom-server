import logging
from django.conf import settings
from django.utils import timezone

from django_elasticsearch_dsl_drf.wrappers import obj_to_dict
from rest_framework import serializers

from api.documents.message import MessageDocument
from etl.providers.factory import import_provider_factory
from core.models import Account, File, Message, Attachments, MessageAudit, User, Label

logger = logging.getLogger(__file__)


def file_exists(filename):
    provider = import_provider_factory(provider=settings.CLOUD_SERVICE_PROVIDER)
    storage_provider = provider(file_path=filename)
    if not storage_provider.exists:
        raise serializers.ValidationError(f"The file {filename} does not exist.")


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
    account = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    filename = serializers.CharField(max_length=200, validators=[file_exists])

    class Meta:
        model = File
        fields = ["account", "filename"]

    def to_representation(self, instance: File):
        return {
            "account": instance.account,
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
        fields = ["title", "files"]

    def create(self, validated_data):
        account, _ = Account.objects.get_or_create(**validated_data)
        return account

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        return instance

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
            "labels": list(Label.objects.all().values("type", "name")),
        }


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = "__all__"


class MessageAuditSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, required=False)
    append_user_label = serializers.CharField(max_length=64, required=False)

    def validate(self, data):
        is_record = data.get("is_record")
        if is_record is False:
            # if user determines something is not a record,
            # validate that they have not also set a redaction or restriction
            needs_redaction = data.get("needs_redaction")
            is_restricted = data.get("is_restricted")
            if is_restricted is True or needs_redaction is True:
                raise serializers.ValidationError(
                    "A message cannot be a non-record and have redactions or restrictions"
                )
        return data

    def update(self, instance, validated_data):
        instance.processed = True
        instance.date_processed = timezone.now()
        instance.updated_by = validated_data["updated_by"]
        if "is_record" in validated_data:
            instance.is_record = validated_data["is_record"]
        if "restricted_until" in validated_data:
            instance.restricted_until = validated_data["restricted_until"]
        if "is_restricted" in validated_data:
            instance.is_restricted = validated_data["is_restricted"]
        if "needs_redaction" in validated_data:
            instance.needs_redaction = validated_data["needs_redaction"]
        if "append_user_label" in validated_data:
            label, _ = Label.objects.get_or_create(
                name=validated_data["append_user_label"], type=Label.USER
            )
            instance.labels.add(label)
        instance.save()
        return instance

    def get_labels(self, obj):
        return obj.labels_indexing

    class Meta:
        model = MessageAudit
        fields = [
            "processed",
            "is_record",
            "date_processed",
            "is_restricted",
            "needs_redaction",
            "restricted_until",
            "updated_by",
            "labels",
            "append_user_label",
        ]
        read_only_fields = ["processed", "date_processed", "updated_by"]


class MessageSerializer(serializers.ModelSerializer):
    audit = MessageAuditSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, obj):
        return Attachments.objects.filter(message=obj)

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
            "audit",
            "attachments",
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
    highlight = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    processed = serializers.SerializerMethodField(method_name="get_processed")
    audit = serializers.SerializerMethodField()

    def get_highlight(self, obj):
        if hasattr(obj.meta, "highlight"):
            return obj.meta.highlight.__dict__["_d_"]
        return {}

    def get_score(self, obj):
        return obj.meta.score

    def get_processed(self, obj):
        if obj.audit:
            return obj.audit.processed
        return False

    def get_audit(self, obj):
        return obj_to_dict(obj.audit)["_d_"]

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
            "audit",
        )
