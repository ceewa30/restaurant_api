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

from menu.serializers import (
    MenuSerializer,
    MenuSerializerDetail,
)

MENUS_URL = reverse('menu:menu-list')


def detail_url(menu_id):
    """Return the detail URL for a menu."""
    return reverse('menu:menu-detail', args=[menu_id])


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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test123')

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
        other_user = create_user(
            email='other@example.com',
            password='password123'
            )
        create_menu(user=other_user)
        create_menu(user=self.user)

        res = self.client.get(MENUS_URL)

        menus = Menu.objects.filter(user=self.user)
        serializer = MenuSerializer(menus, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_menu_details(self):
        """Test get menu details."""
        menu = create_menu(user=self.user)

        url = detail_url(menu.id)
        res = self.client.get(url)

        serializer = MenuSerializerDetail(menu)
        self.assertEqual(res.data, serializer.data)

    def test_create_menu(self):
        """Test creating a menu."""
        payload = {
            'title': 'New menu',
            'time_minutes': 60,
            'price': Decimal('20.00'),
        }
        # /api/menus/menu
        res = self.client.post(MENUS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        menu = Menu.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(menu, k), v)
        self.assertEqual(menu.user, self.user)

    def test_partial_update(self):
        """Test partial update of a menu."""
        menu = create_menu(user=self.user, title='Old menu')

        url = detail_url(menu.id)
        payload = {'title': 'Updated menu'}

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        self.assertEqual(menu.title, payload['title'])
        self.assertEqual(menu.user, self.user)

    def test_full_update(self):
        """Test full update of menu."""
        menu = create_menu(user=self.user, title='Old menu')

        url = detail_url(menu.id)
        payload = {
            'title': 'Updated menu',
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'description': 'Updated description',
        }

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(menu, k), v)
        self.assertEqual(menu.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the menu user results in an error."""
        menu = create_menu(user=self.user)

        url = detail_url(menu.id)
        payload = {'user': create_user(
            email='new@example.com',
            password='test123').id}

        self.client.patch(url, payload)

        menu.refresh_from_db()
        self.assertEqual(menu.user, self.user)

    def test_delete_menu(self):
        """Test deleting a menu successful."""
        menu = create_menu(user=self.user)

        url = detail_url(menu.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(id=menu.id).exists())

    def test_delete_other_users_menu_error(self):
        """Test trying to delete another users menu gives error."""
        other_user = create_user(
            email='other@example.com',
            password='password123'
            )
        menu = create_menu(user=other_user)

        url = detail_url(menu.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Menu.objects.filter(id=menu.id).exists())
