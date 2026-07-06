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

    from datetime import datetime
    import pytz

    bogota_tz = pytz.timezone('America/Bogota')

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
    current = bogota_tz.localize(datetime.combine(selected_date, schedule.start_time))
    end = bogota_tz.localize(datetime.combine(selected_date, schedule.end_time))

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
            apt_start = apt.start_datetime.astimezone(bogota_tz)
            apt_end = apt.end_datetime.astimezone(bogota_tz)
            if current < apt_end and slot_end > apt_start:
                is_available = False
                break

        if is_available:
            for block in time_blocks_list:
                block_start = block.start_datetime.astimezone(bogota_tz)
                block_end = block.end_datetime.astimezone(bogota_tz)
                if current < block_end and slot_end > block_start:
                    is_available = False
                    break

        if is_available:
            slots.append(current.strftime('%H:%M'))

        current += duration

    return Response({'date': date_str, 'slots': slots})


@api_view(['GET'])
@permission_classes([AllowAny])
def public_business(request, business_slug):
    try:
        business = Business.objects.get(slug=business_slug, is_active=True)
    except Business.DoesNotExist:
        return Response({'error': 'Negocio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    from businesses.serializers import BusinessSerializer, ServiceSerializer, ProfessionalSerializer
    data = {
        'business': BusinessSerializer(business).data,
        'services': ServiceSerializer(business.services.filter(is_active=True), many=True).data,
        'professionals': ProfessionalSerializer(business.professionals.filter(is_active=True), many=True).data,
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_appointment(request, business_slug):
    try:
        business = Business.objects.get(slug=business_slug, is_active=True)
    except Business.DoesNotExist:
        return Response({'error': 'Negocio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    professional_id = request.data.get('professional_id')
    service_id = request.data.get('service_id')
    start_datetime_str = request.data.get('start_datetime')
    client_name = request.data.get('client_name')
    client_phone = request.data.get('client_phone')

    if not all([professional_id, service_id, start_datetime_str, client_name, client_phone]):
        return Response({'error': 'Faltan campos obligatorios: professional_id, service_id, start_datetime, client_name, client_phone'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        professional = business.professionals.get(pk=professional_id, is_active=True)
        service = business.services.get(pk=service_id, is_active=True)
    except (Professional.DoesNotExist, Service.DoesNotExist):
        return Response({'error': 'Profesional o servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    from datetime import datetime
    try:
        start_datetime = datetime.fromisoformat(start_datetime_str)
    except ValueError:
        return Response({'error': 'Formato de fecha invalido. Usa ISO 8601: YYYY-MM-DDTHH:MM:SS'}, status=status.HTTP_400_BAD_REQUEST)

    end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)

    conflict = professional.appointments.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        status__in=['confirmed', 'pending']
    ).exists()

    if conflict:
        return Response({'error': 'Ese horario ya esta ocupado'}, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.create(
        business=business,
        professional=professional,
        service=service,
        client_name=client_name,
        client_phone=client_phone,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status='confirmed'
    )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    try:
        business = Business.objects.get(owner=request.user)
    except Business.DoesNotExist:
        return Response({'error': 'No tienes un negocio registrado'}, status=status.HTTP_404_NOT_FOUND)

    date_str = request.query_params.get('date')
    status_filter = request.query_params.get('status')

    appointments = business.appointments.all().order_by('start_datetime')

    if date_str:
        appointments = appointments.filter(start_datetime__date=date_str)

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    try:
        business = Business.objects.get(owner=request.user)
        appointment = business.appointments.get(pk=pk)
    except (Business.DoesNotExist, Appointment.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        new_status = request.data.get('status')
        notes = request.data.get('notes')

        if new_status:
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no_show']
            if new_status not in valid_statuses:
                return Response({'error': f'Estado inválido. Opciones: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
            appointment.status = new_status

        if notes is not None:
            appointment.notes = notes

        appointment.save()
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_appointment(request):
    try:
        business = Business.objects.get(owner=request.user)
    except Business.DoesNotExist:
        return Response({'error': 'No tienes un negocio registrado'}, status=status.HTTP_404_NOT_FOUND)

    professional_id = request.data.get('professional_id')
    service_id = request.data.get('service_id')
    start_datetime_str = request.data.get('start_datetime')
    client_name = request.data.get('client_name')
    client_phone = request.data.get('client_phone')

    if not all([professional_id, service_id, start_datetime_str, client_name, client_phone]):
        return Response({'error': 'Faltan campos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        professional = business.professionals.get(pk=professional_id, is_active=True)
        service = business.services.get(pk=service_id, is_active=True)
    except (Professional.DoesNotExist, Service.DoesNotExist):
        return Response({'error': 'Profesional o servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    from datetime import datetime
    try:
        start_datetime = datetime.fromisoformat(start_datetime_str)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Usa ISO 8601: YYYY-MM-DDTHH:MM:SS'}, status=status.HTTP_400_BAD_REQUEST)

    end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)

    conflict = professional.appointments.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        status__in=['confirmed', 'pending']
    ).exists()

    if conflict:
        return Response({'error': 'Ese horario ya está ocupado'}, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.create(
        business=business,
        professional=professional,
        service=service,
        client_name=client_name,
        client_phone=client_phone,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status='confirmed',
        notes=request.data.get('notes', '')
    )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)