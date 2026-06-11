from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Task, Status, Priority
from .serializers import TaskSerializer, StatusSerializer, PrioritySerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Task.objects.all()
        return Task.objects.filter(assignee=user)

    def perform_create(self, serializer):
        # Автоматически устанавливаем создателя и исполнителя
        serializer.save(
            created_by=self.request.user,
            assignee=self.request.user
        )


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [IsAuthenticated]