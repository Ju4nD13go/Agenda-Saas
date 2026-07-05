from rest_framework import serializers
from .models import Business, Professional, Service
from django.utils.text import slugify


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            'id', 'name', 'slug', 'description',
            'address', 'phone', 'logo_url',
            'timezone', 'currency', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('slug', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id', 'name', 'description', 'duration_minutes',
            'price', 'category', 'is_active', 'created_at'
        )
        read_only_fields = ('created_at',)

class ProfessionalSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Service.objects.all(), write_only=True, source='services'
    )

    class Meta:
        model = Professional
        fields = (
            'id', 'full_name', 'email', 'bio',
            'photo_url', 'services', 'service_ids',
            'is_active', 'created_at'
        )
        read_only_fields = ('created_at',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email