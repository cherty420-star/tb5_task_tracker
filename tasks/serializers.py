from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Task, Status, Priority

User = get_user_model()


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'name', 'level']


class UserSimpleSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для пользователя"""

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'position', 'role']


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка задач (краткий)"""
    status = StatusSerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)
    assignee = UserSimpleSerializer(read_only=True)
    parent_task_id = serializers.IntegerField(source='parent_task.id', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'priority', 'assignee',
                  'parent_task_id', 'deadline', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Полный сериализатор для задач"""
    status = StatusSerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)
    assignee = UserSimpleSerializer(read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    parent_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True
    )
    subtasks_count = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'created_by', 'parent_task', 'subtasks_count',
            'is_overdue', 'created_at', 'updated_at', 'deadline'
        ]

    def get_subtasks_count(self, obj):
        return obj.subtasks.count()

    def validate_deadline(self, value):
        """Валидация: дедлайн не может быть в прошлом"""
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом")
        return value

    def validate_parent_task(self, value):
        """Валидация: нельзя назначить родителем самого себя"""
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError("Нельзя назначить задачу родителем самой себя")
        return value

    def validate(self, data):
        """Комплексная валидация"""
        # Проверка: если задача имеет родителя, статус не может быть "Завершена"
        if data.get('parent_task'):
            status = data.get('status') or (self.instance.status if self.instance else None)
            if status and status.name == 'Завершена':
                raise serializers.ValidationError(
                    "Задача с родительской зависимостью не может быть завершена"
                )

        # Проверка: если задача завершена, у неё не должно быть активных подзадач
        status = data.get('status') or (self.instance.status if self.instance else None)
        if status and status.name == 'Завершена' and self.instance and self.instance.has_active_subtasks:
            raise serializers.ValidationError(
                "Нельзя завершить задачу, у которой есть активные подзадачи"
            )

        return data


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления задач"""
    parent_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True
    )
    status_id = serializers.PrimaryKeyRelatedField(
        source='status',
        queryset=Status.objects.all(),
        required=False,
        allow_null=True
    )
    priority_id = serializers.PrimaryKeyRelatedField(
        source='priority',
        queryset=Priority.objects.all(),
        required=False,
        allow_null=True
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.filter(role='employee'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status_id', 'priority_id',
            'assignee_id', 'parent_task', 'deadline'
        ]

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом")
        return value

    def validate_parent_task(self, value):
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError("Нельзя назначить задачу родителем самой себя")
        return value

    def validate(self, data):
        # Проверка: если задача имеет родителя, статус не может быть "Завершена"
        if data.get('parent_task'):
            status = data.get('status') or (self.instance.status if self.instance else None)
            if status and status.name == 'Завершена':
                raise serializers.ValidationError(
                    "Задача с родительской зависимостью не может быть завершена"
                )
        return data