from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Business
from .serializers import BusinessSerializer


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