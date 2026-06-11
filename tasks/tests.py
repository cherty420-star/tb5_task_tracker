from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task, Status, Priority

User = get_user_model()


class TaskAPITestCase(TestCase):
    """Тесты для API задач"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаём пользователей
        self.employee = User.objects.create_user(
            username='employee1',
            password='testpass123',
            role='employee'
        )
        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='manager'
        )

        # Создаём статусы и приоритеты
        self.status_new = Status.objects.create(name='Новая')
        self.priority_medium = Priority.objects.create(name='Средний', level=2)

        # Создаём задачу для сотрудника
        self.task = Task.objects.create(
            title='Тестовая задача',
            description='Описание тестовой задачи',
            status=self.status_new,
            priority=self.priority_medium,
            assignee=self.employee,
            created_by=self.manager
        )

        # Настраиваем API клиент
        self.client = APIClient()

    def test_employee_can_view_own_tasks(self):
        """Тест: Сотрудник видит только свои задачи"""
        # Авторизуемся как сотрудник
        self.client.force_authenticate(user=self.employee)

        # Запрашиваем список задач
        response = self.client.get('/api/tasks/tasks/')

        # Проверяем
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Тестовая задача')

    def test_employee_cannot_view_others_tasks(self):
        """Тест: Сотрудник не видит задачи других сотрудников"""
        # Создаём другого сотрудника и его задачу
        other_employee = User.objects.create_user(
            username='employee2',
            password='testpass123',
            role='employee'
        )
        Task.objects.create(
            title='Чужая задача',
            description='Эта задача не должна быть видна',
            assignee=other_employee,
            created_by=self.manager
        )

        # Авторизуемся как первый сотрудник
        self.client.force_authenticate(user=self.employee)

        # Запрашиваем список задач
        response = self.client.get('/api/tasks/tasks/')

        # Должна быть только своя задача
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertNotIn('Чужая задача', str(response.data))

    def test_manager_can_view_all_tasks(self):
        """Тест: Руководитель видит все задачи"""
        # Создаём дополнительную задачу
        other_employee = User.objects.create_user(
            username='employee3',
            password='testpass123',
            role='employee'
        )
        Task.objects.create(
            title='Задача другого сотрудника',
            description='Руководитель должен её видеть',
            assignee=other_employee,
            created_by=self.manager
        )

        # Авторизуемся как руководитель
        self.client.force_authenticate(user=self.manager)

        # Запрашиваем список задач
        response = self.client.get('/api/tasks/tasks/')

        # Должны быть обе задачи
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_task_without_auth(self):
        """Тест: Неавторизованный пользователь не может создать задачу"""
        self.client.force_authenticate(user=None)

        data = {
            'title': 'Новая задача без авторизации',
            'description': 'Эта задача не должна создаться'
        }
        response = self.client.post('/api/tasks/tasks/', data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_can_create_task(self):
        """Тест: Сотрудник может создать задачу"""
        self.client.force_authenticate(user=self.employee)

        data = {
            'title': 'Моя новая задача',
            'description': 'Я создал её сам'
        }
        response = self.client.post('/api/tasks/tasks/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Моя новая задача')
        self.assertEqual(response.data['assignee']['username'], self.employee.username)
        self.assertEqual(response.data['created_by']['username'], self.employee.username)

    def test_update_task(self):
        """Тест: Обновление задачи"""
        self.client.force_authenticate(user=self.employee)

        data = {
            'title': 'Обновлённое название задачи'
        }
        response = self.client.patch(f'/api/tasks/tasks/{self.task.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Обновлённое название задачи')

    def test_delete_task(self):
        """Тест: Удаление задачи"""
        self.client.force_authenticate(user=self.employee)

        response = self.client.delete(f'/api/tasks/tasks/{self.task.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.filter(id=self.task.id).count(), 0)