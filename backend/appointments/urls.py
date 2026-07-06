from django.urls import path
from . import views

urlpatterns = [
    path('professionals/<int:professional_id>/schedules/', views.schedules, name='schedules'),
    path('professionals/<int:professional_id>/schedules/<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('professionals/<int:professional_id>/time-blocks/', views.time_blocks, name='time_blocks'),
    path('public/<slug:business_slug>/professionals/<int:professional_id>/services/<int:service_id>/slots/', views.available_slots, name='available_slots'),
    path('public/<slug:business_slug>/', views.public_business, name='public_business'),
    path('public/<slug:business_slug>/book/', views.create_appointment, name='create_appointment'),
]