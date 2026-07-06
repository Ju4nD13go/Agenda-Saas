from django.db import models
from businesses.models import Business, Professional, Service


class Schedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(default=True)

    class Meta:
        unique_together = ('professional', 'day_of_week')

    def __str__(self):
        return f"{self.professional} - {self.get_day_of_week_display()}"


class TimeBlock(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='time_blocks')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.professional} bloqueado {self.start_datetime}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No se presentó'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='appointments')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.service.name} - {self.start_datetime}"