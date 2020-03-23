from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from core import models as ratom

admin.site.register(ratom.Account)


@admin.register(ratom.User)
class CustomUserAdmin(UserAdmin):
    model = ratom.User
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


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
    list_filter = ("is_record", "processed", "message__account")
    search_fields = ("message__body", "pk")
    date_hierarchy = "date_processed"
    ordering = ("-pk",)


@admin.register(ratom.File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "account",
        "filename",
        "reported_total_messages",
        "imported_total_messages",
        "message_errors",
        "total_file_size",
        "date_imported",
        "import_status",
    )
    list_filter = ("import_status", "account")
    ordering = ("-date_imported",)
    search_fields = ("filename", "pk")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_message_count=Count("message", distinct=True),)
        return queryset

    def imported_total_messages(self, obj):
        return obj._message_count

    def message_errors(self, obj):
        return len(obj.errors) if obj.errors else ""

    def total_file_size(self, obj):
        return filesizeformat(obj.file_size)


@admin.register(ratom.Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("pk", "type", "name")
    list_filter = ("type",)
    search_fields = ("type", "name")
    ordering = ("type", "name")
