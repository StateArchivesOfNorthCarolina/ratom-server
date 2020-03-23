from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from typing import List
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
    readonly_fields = ("get_history",)
    list_select_related = ("message",)
    list_filter = ("is_record", "processed")
    search_fields = ("message__body", "pk")
    date_hierarchy = "date_processed"
    ordering = ("-message__sent_date",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("processed", "is_record", "is_restricted", "needs_redaction"),
                )
            },
        ),
        ("Labels", {"fields": ("labels",)}),
        ("History", {"classes": ("collapse",), "fields": ("get_history",)}),
    )

    def get_history(self, instance):
        # import pudb;pudb.set_trace()
        # history = instance.history.intersection()
        # html_table = self._stringify_history(instance.history.all())
        pass

    def _stringify_history(self, histories: List[ratom.HistoricalRecords]):
        history_line = []
        history_line.append("\n\nChanged Field\tBefore Change\tAfter Change\n")
        if len(histories) == 1:
            pass
        else:
            new_record, old_record = histories
            delta = new_record.diff_against(old_record)
            for change in delta.changes:
                history_line.append(
                    f"{change.field}\t" f"{change.old}\t" f"{change.new}\t" f"\n\n"
                )
            return "".join(history_line)


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
