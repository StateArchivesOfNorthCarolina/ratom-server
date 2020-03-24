from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
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
    IGNORE_CHANGES = ["date_processed", "updated_by"]
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
        ("Status", {"fields": (("processed", "is_record", "needs_redaction"),)},),
        ("Restrictions", {"fields": ("is_restricted", "restricted_until")}),
        ("Labels", {"fields": ("labels",)}),
        ("Message History", {"classes": ("collapse",), "fields": ("get_history",)}),
    )

    def get_history(self, instance):
        """
        Returns an html representation of the MessageAudit's history. Not every change is important
        date_processed is a change but doesn't give anymore information than is revealed by the
        Date and Time column.
        :param instance: MessageAudit
        :return: SafeString
        """
        histories = instance.history.all()
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
            else:
                first = histories.last()
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
        Yields pairs of histories. This function assumes a queryset of histories with most recent
        change last in the set. We flip these to print the newest changes first and descend to the
        oldest.
        :param histories:
        :return: tuple(MessageAuditHistory, MessageAuditHistory)
        """
        hist_list = list(histories)
        hist_list.reverse()
        new = None
        old = None
        while len(hist_list) > 1:
            if not new:
                new = hist_list.pop()
                old = hist_list.pop()
            else:
                new = old
                old = hist_list.pop()
            yield new, old
        yield None, None


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
