"""
Serializers for menu APIs
"""
from rest_framework import serializers
from core.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for Menu"""

    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
