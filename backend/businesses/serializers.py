from rest_framework import serializers
from .models import Business
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