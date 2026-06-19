from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Task, Status, Priority

User = get_user_model()


class TaskAdvancedTestCase(TestCase):
    """Тесты для новых фич задач"""

    def setUp(self):
        self.client = APIClient()

        # Создаём пользователей
        self.manager = User.objects.create_user(
            username='manager',
            password='pass123',
            role='manager',
            full_name='Менеджер Тест',
            position='Директор'
        )
        self.employee1 = User.objects.create_user(
            username='emp1',
            password='pass123',
            role='employee',
            full_name='Сотрудник Один',
            position='Разработчик'
        )
        self.employee2 = User.objects.create_user(
            username='emp2',
            password='pass123',
            role='employee',
            full_name='Сотрудник Два',
            position='Тестировщик'
        )

        # Создаём статусы и приоритеты
        self.status_new = Status.objects.create(name='Новая')
        self.status_in_progress = Status.objects.create(name='В работе')
        self.status_done = Status.objects.create(name='Завершена')
        self.priority_high = Priority.objects.create(name='Высокий', level=3)

        # Создаём задачи
        self.task1 = Task.objects.create(
            title='Задача 1',
            status=self.status_new,
            assignee=self.employee1,
            created_by=self.manager
        )
        self.task2 = Task.objects.create(
            title='Задача 2',
            status=self.status_in_progress,
            assignee=self.employee2,
            created_by=self.manager,
            parent_task=self.task1
        )

        self.client.force_authenticate(user=self.manager)

    def test_create_task_with_parent(self):
        """Тест: Создание задачи с родительской задачей"""
        data = {
            'title': 'Подзадача',
            'parent_task': self.task1.id,
            'assignee_id': self.employee1.id
        }
        response = self.client.post('/api/tasks/tasks/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent_task'], self.task1.id)

    def test_cannot_set_self_as_parent(self):
        """Тест: Нельзя назначить задачу родителем самой себя"""
        data = {
            'title': 'Сам себе родитель',
            'parent_task': self.task1.id
        }
        # Пытаемся обновить существующую задачу, указав себя как родителя
        response = self.client.patch(f'/api/tasks/tasks/{self.task1.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('родителем самой себя', str(response.data))

    def test_busy_employees_endpoint(self):
        """Тест: Эндпоинт занятых сотрудников"""
        response = self.client.get('/api/tasks/tasks/busy_employees/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Оба сотрудника с задачами

        # Сортировка: у кого больше задач
        self.assertEqual(response.data[0]['id'], self.employee2.id)  # У него 1 задача в работе

    def test_important_tasks_endpoint(self):
        """Тест: Эндпоинт важных задач"""
        # Создаём важную задачу: Новая, но с подзадачей в работе
        important_task = Task.objects.create(
            title='Важная задача',
            status=self.status_new,
            assignee=self.employee1,
            created_by=self.manager
        )
        Task.objects.create(
            title='Подзадача важной',
            status=self.status_in_progress,
            assignee=self.employee2,
            created_by=self.manager,
            parent_task=important_task
        )

        response = self.client.get('/api/tasks/tasks/important_tasks/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], 'Важная задача')

    def test_cannot_complete_task_with_active_subtasks(self):
        """Тест: Нельзя завершить задачу с активными подзадачами"""
        # Создаём задачу с подзадачей
        parent = Task.objects.create(
            title='Родитель',
            status=self.status_new,
            assignee=self.employee1,
            created_by=self.manager
        )
        Task.objects.create(
            title='Подзадача',
            status=self.status_in_progress,
            assignee=self.employee2,
            created_by=self.manager,
            parent_task=parent
        )

        # Пытаемся завершить родительскую задачу
        response = self.client.patch(
            f'/api/tasks/tasks/{parent.id}/',
            {'status_id': self.status_done.id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('активные подзадачи', str(response.data))

    def test_deadline_validation(self):
        """Тест: Валидация дедлайна в прошлом"""
        past_deadline = (timezone.now() - timedelta(days=1)).isoformat()
        data = {
            'title': 'Задача с прошлым дедлайном',
            'deadline': past_deadline
        }
        response = self.client.post('/api/tasks/tasks/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Дедлайн не может быть в прошлом', str(response.data))