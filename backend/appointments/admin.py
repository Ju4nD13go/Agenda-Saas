from django.contrib import admin
from .models import Schedule, TimeBlock, Appointment


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('professional', 'day_of_week', 'start_time', 'end_time', 'is_working')
    list_filter = ('is_working', 'day_of_week')


@admin.register(TimeBlock)
class TimeBlockAdmin(admin.ModelAdmin):
    list_display = ('professional', 'start_datetime', 'end_datetime', 'reason')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service', 'professional', 'start_datetime', 'status')
    list_filter = ('status',)
    search_fields = ('client_name', 'client_email')