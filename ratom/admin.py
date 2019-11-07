from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Collection, Processor, Message

admin.site.register(User, UserAdmin)
admin.site.register(Collection)
admin.site.register(Processor)
admin.site.register(Message)