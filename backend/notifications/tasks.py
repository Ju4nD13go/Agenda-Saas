from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from .services import send_reminder


@shared_task
def send_reminder_24h():
    now = timezone.now()
    target_start = now + timedelta(hours=24)
    target_end = target_start + timedelta(minutes=30)

    appointments = Appointment.objects.filter(
        start_datetime__gte=target_start,
        start_datetime__lt=target_end,
        status='confirmed'
    ).exclude(notifications__type='reminder_24h', notifications__status='sent')

    for appointment in appointments:
        send_reminder(appointment, hours_before=24)

    return f"{appointments.count()} recordatorios 24h enviados"


@shared_task
def send_reminder_1h():
    now = timezone.now()
    target_start = now + timedelta(hours=1)
    target_end = target_start + timedelta(minutes=30)

    appointments = Appointment.objects.filter(
        start_datetime__gte=target_start,
        start_datetime__lt=target_end,
        status='confirmed'
    ).exclude(notifications__type='reminder_1h', notifications__status='sent')

    for appointment in appointments:
        send_reminder(appointment, hours_before=1)

    return f"{appointments.count()} recordatorios 1h enviados"