from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from .models import Task, Status, Priority
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskCreateUpdateSerializer,
    StatusSerializer, PrioritySerializer
)

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD для задач с дополнительными эндпоинтами:
    - busy_employees: занятые сотрудники
    - important_tasks: важные задачи
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        """Права доступа: сотрудник видит свои задачи, руководитель - все"""
        user = self.request.user
        queryset = Task.objects.select_related(
            'status', 'priority', 'assignee', 'created_by', 'parent_task'
        ).prefetch_related('subtasks')

        if user.role == 'manager':
            return queryset

        # Сотрудник видит только свои задачи
        return queryset.filter(assignee=user)

    def perform_create(self, serializer):
        """При создании: создатель = текущий пользователь, исполнитель = он же или указанный"""
        assignee = serializer.validated_data.get('assignee')
        if not assignee:
            assignee = self.request.user
        serializer.save(
            created_by=self.request.user,
            assignee=assignee
        )

    @action(detail=False, methods=['get'])
    def busy_employees(self, request):
        """
        Список сотрудников с количеством активных задач
        GET /api/tasks/tasks/busy_employees/
        """
        # Активные статусы: Новая, В работе
        active_statuses = Status.objects.filter(name__in=['Новая', 'В работе'])

        employees = User.objects.filter(
            role='employee',
            tasks__status__in=active_statuses
        ).annotate(
            active_tasks_count=Count('tasks', filter=Q(tasks__status__in=active_statuses))
        ).order_by('-active_tasks_count')

        data = [{
            'id': emp.id,
            'full_name': emp.full_name,
            'position': emp.position,
            'active_tasks_count': emp.active_tasks_count,
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status.name if task.status else None,
                    'deadline': task.deadline
                }
                for task in emp.tasks.filter(status__in=active_statuses)
            ]
        } for emp in employees if emp.active_tasks_count > 0]

        return Response(data)

    @action(detail=False, methods=['get'])
    def important_tasks(self, request):
        """
        Важные задачи:
        - задачи, которые не взяты в работу (статус 'Новая')
        - но от которых зависят другие задачи в работе
        - подбор сотрудников по правилам загрузки
        GET /api/tasks/tasks/important_tasks/
        """
        # Статусы
        new_status = Status.objects.filter(name='Новая').first()
        in_progress_status = Status.objects.filter(name='В работе').first()

        if not new_status or not in_progress_status:
            return Response(
                {"detail": "Не найдены статусы 'Новая' или 'В работе'"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Важные задачи: Новая, у которых есть подзадачи в работе
        important = Task.objects.filter(
            status=new_status,
            subtasks__status=in_progress_status
        ).distinct().select_related('assignee')

        data = []
        for task in important:
            # Ищем сотрудников, которые могут взять задачу
            # (у кого меньше всего активных задач)
            available_employees = User.objects.filter(
                role='employee'
            ).annotate(
                active_count=Count('tasks', filter=Q(tasks__status__in=[new_status, in_progress_status]))
            ).order_by('active_count')[:3]

            data.append({
                'task': task.title,
                'deadline': task.deadline,
                'employees': [emp.full_name for emp in available_employees]
            })

        return Response(data)


class StatusViewSet(viewsets.ModelViewSet):
    """CRUD для статусов"""
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]


class PriorityViewSet(viewsets.ModelViewSet):
    """CRUD для приоритетов"""
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [IsAuthenticated]