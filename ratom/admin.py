from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Collection, Processor, Message

admin.site.register(User, UserAdmin)
admin.site.register(Collection)
admin.site.register(Processor)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "msg_to",
        "sent_date",
        "msg_subject",
        "collection",
    )
    list_filter = ("sent_date", "collection")
    search_fields = ("msg_body",)
    date_hierarchy = "sent_date"
    ordering = ("-sent_date",)
