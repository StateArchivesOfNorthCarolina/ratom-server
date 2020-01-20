from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, Processor, Message

admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Processor)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "msg_to",
        "msg_from",
        "sent_date",
        "subject",
        "account",
    )
    list_filter = ("sent_date", "account")
    search_fields = ("body",)
    date_hierarchy = "sent_date"
    ordering = ("-sent_date",)
