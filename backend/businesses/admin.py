from django.contrib import admin
from .models import Business, Professional, Service


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'duration_minutes', 'price', 'is_active')
    search_fields = ('name', 'business__name')
    list_filter = ('is_active', 'category')

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'is_active', 'created_at')
    search_fields = ('user__email', 'business__name')
    list_filter = ('is_active',)
    filter_horizontal = ('services',)