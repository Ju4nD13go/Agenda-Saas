from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Business, Service, Professional
from .serializers import BusinessSerializer, ServiceSerializer, ProfessionalSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_business(request):
    serializer = BusinessSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_business(request):
    try:
        business = Business.objects.get(owner=request.user)
    except Business.DoesNotExist:
        return Response({'error': 'No tienes un negocio registrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessSerializer(business)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def services(request):
    try:
        business = Business.objects.get(owner=request.user)
    except Business.DoesNotExist:
        return Response({'error': 'No tienes un negocio registrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        all_services = business.services.all()
        serializer = ServiceSerializer(all_services, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(business=business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def service_detail(request, pk):
    try:
        business = Business.objects.get(owner=request.user)
        service = business.services.get(pk=pk)
    except (Business.DoesNotExist, Service.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        service.is_active = False
        service.save()
        return Response({'message': 'Servicio desactivado'}, status=status.HTTP_200_OK)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def professionals(request):
    try:
        business = Business.objects.get(owner=request.user)
    except Business.DoesNotExist:
        return Response({'error': 'No tienes un negocio registrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        all_professionals = business.professionals.filter(is_active=True)
        serializer = ProfessionalSerializer(all_professionals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        email = request.data.get('email')
        try:
            from users.models import User
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No existe un usuario con ese email'}, status=status.HTTP_404_NOT_FOUND)

        if Professional.objects.filter(user=user, business=business).exists():
            return Response({'error': 'Este profesional ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

        professional = Professional.objects.create(
            business=business,
            user=user,
            bio=request.data.get('bio', ''),
            photo_url=request.data.get('photo_url', ''),
        )
        service_ids = request.data.get('service_ids', [])
        if service_ids:
            professional.services.set(service_ids)

        serializer = ProfessionalSerializer(professional)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def professional_detail(request, pk):
    try:
        business = Business.objects.get(owner=request.user)
        professional = business.professionals.get(pk=pk)
    except (Business.DoesNotExist, Professional.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ProfessionalSerializer(professional, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        professional.is_active = False
        professional.save()
        return Response({'message': 'Profesional desactivado'}, status=status.HTTP_200_OK)