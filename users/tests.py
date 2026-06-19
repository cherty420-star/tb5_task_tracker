from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()


class EmployeeCRUDTestCase(TestCase):
    """Тесты для CRUD сотрудников"""

    def setUp(self):
        self.client = APIClient()

        # Создаём менеджера и сотрудника
        self.manager = User.objects.create_user(
            username='manager1',
            password='pass123',
            role='manager',
            full_name='Менеджер М.М.',
            position='Директор'
        )
        self.employee = User.objects.create_user(
            username='employee1',
            password='pass123',
            role='employee',
            full_name='Сотрудник С.С.',
            position='Разработчик'
        )

    def test_manager_can_list_employees(self):
        """Тест: Менеджер может получить список сотрудников"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/users/employees/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'employee1')

    def test_employee_cannot_list_employees(self):
        """Тест: Сотрудник не может получить список сотрудников"""
        self.client.force_authenticate(user=self.employee)
        response = self.client.get('/api/users/employees/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_manager_can_create_employee(self):
        """Тест: Менеджер может создать сотрудника"""
        self.client.force_authenticate(user=self.manager)
        data = {
            'username': 'new_employee',
            'password': 'pass123',
            'full_name': 'Новый Сотрудник',
            'position': 'Тестировщик'
        }
        response = self.client.post('/api/users/employees/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'new_employee')
        self.assertEqual(response.data['role'], 'employee')

    def test_manager_can_update_employee(self):
        """Тест: Менеджер может обновить данные сотрудника"""
        self.client.force_authenticate(user=self.manager)
        data = {'position': 'Старший разработчик'}
        response = self.client.patch(f'/api/users/employees/{self.employee.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 'Старший разработчик')

    def test_manager_can_delete_employee(self):
        """Тест: Менеджер может удалить сотрудника"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/users/employees/{self.employee.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.employee.id).exists())

    def test_manager_cannot_delete_self(self):
        """Тест: Менеджер не может удалить самого себя"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/users/employees/{self.manager.id}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=self.manager.id).exists())


class CurrentUserTestCase(TestCase):
    """Тесты для текущего пользователя"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            role='employee',
            full_name='Тестовый Пользователь',
            position='Инженер'
        )

    def test_get_current_user(self):
        """Тест: Получение информации о текущем пользователе"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['full_name'], 'Тестовый Пользователь')

    def test_update_current_user(self):
        """Тест: Обновление информации о текущем пользователе"""
        self.client.force_authenticate(user=self.user)
        data = {'position': 'Ведущий инженер'}
        response = self.client.patch('/api/users/me/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 'Ведущий инженер')