from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Business, Service
from .serializers import BusinessSerializer, ServiceSerializer


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