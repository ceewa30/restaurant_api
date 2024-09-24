"""
Views for the menu APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Menu
from menu import serializers


class MenuViewSet(viewsets.ModelViewSet):
    """View for manage Menu APIs."""

    serializer_class = serializers.MenuSerializer
    queryset = Menu.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve menus for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
