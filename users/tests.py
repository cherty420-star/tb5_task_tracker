from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserAPITestCase(TestCase):
    """Тесты для API пользователей"""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Тест: Регистрация нового пользователя"""
        data = {
            'username': 'newuser',
            'password': 'strongpass123',
            'password2': 'strongpass123',
            'role': 'employee'
        }
        response = self.client.post('/api/users/register/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['role'], 'employee')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_with_password_mismatch(self):
        """Тест: Ошибка при несовпадении паролей"""
        data = {
            'username': 'testuser',
            'password': 'pass123',
            'password2': 'pass456',
            'role': 'employee'
        }
        response = self.client.post('/api/users/register/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Тест: Ошибка при создании пользователя с существующим именем"""
        User.objects.create_user(username='existing', password='pass123')

        data = {
            'username': 'existing',
            'password': 'pass123',
            'password2': 'pass123',
            'role': 'employee'
        }
        response = self.client.post('/api/users/register/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token(self):
        """Тест: Получение JWT токена"""
        User.objects.create_user(username='testuser', password='testpass123')

        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/users/token/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)