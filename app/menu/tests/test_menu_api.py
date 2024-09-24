"""
Tests for menu APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Menu

from menu.serializers import MenuSerializer

MENUS_URL = reverse('menu:menu-list')


def create_menu(user, **params):
    """Create and return a sample menu."""
    defaults = {
        'title': 'Sample menu',
        'time_minutes': 30,
        'price': Decimal('15.00'),
        'description': 'This is a sample menu.',
    }
    defaults.update(params)

    menu = Menu.objects.create(user=user, **defaults)
    return menu


class PublicMenuAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(MENUS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMenuAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
        )
        self.client.force_authenticate(self.user)

    def test_retrive_menu(self):
        """Test retrieving a list of menus."""
        create_menu(user=self.user)
        create_menu(user=self.user)

        res = self.client.get(MENUS_URL)

        menus = Menu.objects.all().order_by('-id')
        serializer = MenuSerializer(menus, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_menu_list_limited_to_user(self):
        """Test list of menus is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_menu(user=other_user)
        create_menu(user=self.user)

        res = self.client.get(MENUS_URL)

        menus = Menu.objects.filter(user=self.user)
        serializer = MenuSerializer(menus, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
