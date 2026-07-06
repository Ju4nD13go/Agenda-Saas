import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-reminder-24h': {
        'task': 'notifications.tasks.send_reminder_24h',
        'schedule': crontab(minute='*/30'),
    },
    'send-reminder-1h': {
        'task': 'notifications.tasks.send_reminder_1h',
        'schedule': crontab(minute='*/15'),
    },
}