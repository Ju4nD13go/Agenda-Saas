from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'type', 'channel', 'status', 'sent_at')
    list_filter = ('type', 'channel', 'status')
    search_fields = ('appointment__client_name',)