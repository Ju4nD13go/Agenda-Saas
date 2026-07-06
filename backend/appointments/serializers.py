from rest_framework import serializers
from .models import Schedule, TimeBlock, Appointment


class ScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_working')


class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = ('id', 'start_datetime', 'end_datetime', 'reason')


class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    professional_name = serializers.CharField(source='professional.user.get_full_name', read_only=True)
    duration_minutes = serializers.IntegerField(source='service.duration_minutes', read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'client_name', 'client_phone',
            'service', 'service_name', 'professional', 'professional_name',
            'start_datetime', 'end_datetime', 'duration_minutes',
            'status', 'notes', 'created_at'
        )
        read_only_fields = ('end_datetime', 'created_at')