from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_business, name='create_business'),
    path('me/', views.my_business, name='my_business'),
    path('me/services/', views.services, name='services'),
    path('me/services/<int:pk>/', views.service_detail, name='service_detail'),
    path('me/professionals/', views.professionals, name='professionals'),
    path('me/professionals/<int:pk>/', views.professional_detail, name='professional_detail'),
]