from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core import models as ratom

admin.site.register(ratom.User, UserAdmin)
admin.site.register(ratom.Account)


@admin.register(ratom.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "source_id",
        "msg_to",
        "msg_from",
        "sent_date",
        "subject",
        "account",
    )
    list_filter = ("sent_date", "account")
    search_fields = ("body", "source_id")
    date_hierarchy = "sent_date"
    raw_id_fields = ("audit", "file")
    ordering = ("-sent_date",)


@admin.register(ratom.MessageAudit)
class MessageAuditAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "message",
        "processed",
        "is_record",
        "date_processed",
        "updated_by",
    )
    list_select_related = ("message",)
    list_filter = ("is_record", "processed")
    search_fields = ("message__body", "pk")
    date_hierarchy = "date_processed"
    ordering = ("-message__sent_date",)


@admin.register(ratom.File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "account",
        "filename",
        "reported_total_messages",
        "date_imported",
        "import_status",
    )
    list_filter = ("import_status", "account")
    ordering = ("-date_imported",)
    search_fields = ("filename", "pk")


@admin.register(ratom.Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("pk", "type", "name")
    list_filter = ("type",)
    search_fields = ("type", "name")
    ordering = ("type", "name")
