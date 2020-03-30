from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from core import models as ratom


@admin.register(ratom.Account)
class AccountAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("title",)


@admin.register(ratom.User)
class CustomUserAdmin(UserAdmin):
    model = ratom.User
    list_display = (
        "pk",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(ratom.Message)
class MessageAdmin(admin.ModelAdmin):
    IGNORE_CHANGES = ["date_processed", "updated_by"]
    list_display = (
        "pk",
        "source_id",
        "msg_to",
        "msg_from",
        "sent_date",
        "subject",
        "account",
    )

    readonly_fields = (
        "get_history",
        "inserted_on",
        "directory",
        "source_id",
        "sent_date",
        "subject",
        "msg_to",
        "msg_from",
        "msg_cc",
        "msg_bcc",
        "body",
        "errors",
        "account",
        "file",
        "headers",
    )
    list_filter = ("sent_date", "account")
    search_fields = ("body", "source_id")
    date_hierarchy = "sent_date"
    raw_id_fields = ("audit", "file")
    ordering = ("-sent_date",)

    fieldsets = (
        ("Message Metadata", {"fields": ("account", "file", "inserted_on")}),
        ("Headers", {"classes": ("collapse",), "fields": ("headers",),}),
        (
            "Message",
            {
                "classes": ("collapse",),
                "fields": (
                    "directory",
                    "source_id",
                    "sent_date",
                    "subject",
                    "msg_to",
                    "msg_from",
                    "msg_cc",
                    "msg_bcc",
                    "body",
                ),
            },
        ),
        ("Errors", {"classes": ("collapse",), "fields": ("errors",)}),
        ("Message History", {"fields": ("audit", "get_history",)}),
    )

    def get_history(self, instance):
        """
        Returns an html representation of the MessageAudit's history. Not every change is important
        date_processed is a change but doesn't give anymore information than is revealed by the
        Date and Time column.
        :param instance: MessageAudit
        :return: SafeString
        """
        histories = instance.audit.history.all().order_by("history_date")
        history_line = "<table><tr><th>Date and Time</th><th>Field</th><th>Changed From</th><th>Changed To</th><th>User</th></tr>"
        for new_record, old_record in self._get_history_pairs(histories):
            if new_record:
                delta = new_record.diff_against(old_record)
                for change in delta.changes:
                    if change.field not in self.IGNORE_CHANGES:
                        history_line += (
                            f"<tr>"
                            f"<td>{new_record.history_date.strftime('%Y-%m-%d %H:%M:%S')}</td>"
                            f"<td>{change.field}</td>"
                            f"<td>{change.old}</td>"
                            f"<td>{change.new}</td>"
                            f"<td>{ratom.User.objects.filter(pk=new_record.updated_by_id).first()}"
                            f"</tr>"
                        )
        first = histories.first()
        history_line += (
            f"<tr>"
            f"<td>{first.history_date.strftime('%Y-%m-%d %H:%M:%S')}</td>"
            f"<td colspan=3>Message Imported</td>"
            f"</tr>"
        )
        history_line += "</table>"
        return format_html(history_line)

    def _get_history_pairs(self, histories):
        """
        Yields pairs of histories. This function assumes a queryset of histories with the oldest entry
        first in the set.
        :param histories:
        :return: tuple(MessageAuditHistory, MessageAuditHistory)
        """
        new = None
        old = None
        hist_list = list(histories)
        if len(hist_list) == 1:
            yield None, hist_list.pop()
        while hist_list:
            new = old
            if not new:
                new = hist_list.pop()
            old = hist_list.pop()
            yield new, old


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

    fieldsets = (
        ("Status", {"fields": (("processed", "is_record", "needs_redaction"),)},),
        ("Restrictions", {"fields": ("is_restricted", "restricted_until")}),
        ("Labels", {"fields": ("labels",)}),
    )


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
    readonly_fields = ("account",)
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
