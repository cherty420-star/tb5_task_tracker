from rest_framework import serializers
from .models import Task, Status, Priority
from django.contrib.auth import get_user_model

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
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class TaskSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)
    assignee = UserSimpleSerializer(read_only=True)
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority',
                  'assignee', 'created_by', 'created_at', 'updated_at', 'deadline']