from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from businesses.models import Business, Professional, Service
from .models import Schedule, TimeBlock, Appointment
from .serializers import ScheduleSerializer, TimeBlockSerializer, AppointmentSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def schedules(request, professional_id):
    try:
        business = Business.objects.get(owner=request.user)
        professional = business.professionals.get(pk=professional_id)
    except (Business.DoesNotExist, Professional.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        all_schedules = professional.schedules.all().order_by('day_of_week')
        serializer = ScheduleSerializer(all_schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def schedule_detail(request, professional_id, pk):
    try:
        business = Business.objects.get(owner=request.user)
        professional = business.professionals.get(pk=professional_id)
        schedule = professional.schedules.get(pk=pk)
    except (Business.DoesNotExist, Professional.DoesNotExist, Schedule.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        schedule.delete()
        return Response({'message': 'Horario eliminado'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def time_blocks(request, professional_id):
    try:
        business = Business.objects.get(owner=request.user)
        professional = business.professionals.get(pk=professional_id)
    except (Business.DoesNotExist, Professional.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        blocks = professional.time_blocks.filter(end_datetime__gte=timezone.now())
        serializer = TimeBlockSerializer(blocks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TimeBlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_slots(request, business_slug, professional_id, service_id):
    try:
        business = Business.objects.get(slug=business_slug)
        professional = business.professionals.get(pk=professional_id, is_active=True)
        service = business.services.get(pk=service_id, is_active=True)
    except (Business.DoesNotExist, Professional.DoesNotExist, Service.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    date_str = request.query_params.get('date')
    if not date_str:
        return Response({'error': 'Debes enviar el parámetro date (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

    from datetime import datetime, date, time
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

    day_of_week = selected_date.weekday()
    try:
        schedule = professional.schedules.get(day_of_week=day_of_week, is_working=True)
    except Schedule.DoesNotExist:
        return Response({'slots': []})

    duration = timedelta(minutes=service.duration_minutes)
    slots = []
    current = datetime.combine(selected_date, schedule.start_time)
    end = datetime.combine(selected_date, schedule.end_time)

    existing_appointments = professional.appointments.filter(
        start_datetime__date=selected_date,
        status__in=['confirmed', 'pending']
    )
    time_blocks_list = professional.time_blocks.filter(
        start_datetime__date=selected_date
    )

    while current + duration <= end:
        slot_end = current + duration
        is_available = True

        for apt in existing_appointments:
            if current < apt.end_datetime.replace(tzinfo=None) and slot_end > apt.start_datetime.replace(tzinfo=None):
                is_available = False
                break

        if is_available:
            for block in time_blocks_list:
                if current < block.end_datetime.replace(tzinfo=None) and slot_end > block.start_datetime.replace(tzinfo=None):
                    is_available = False
                    break

        if is_available:
            slots.append(current.strftime('%H:%M'))

        current += duration

    return Response({'date': date_str, 'slots': slots})