"""
Serializers for menu APIs
"""
from rest_framework import serializers
from core.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for Menu"""

    class Meta:
        model = Menu
        fields = ['id', 'title', 'time_minutes', 'price']
        read_only_fields = ['id', 'created_at']


class MenuSerializerDetail(MenuSerializer):
    """Serializer for menu detail view"""

    class Meta(MenuSerializer.Meta):
        fields = MenuSerializer.Meta.fields + ['description']
