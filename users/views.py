from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    EmployeeSerializer,
    EmployeeCreateSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD для сотрудников (только для менеджеров)
    GET /api/users/employees/ - список сотрудников
    POST /api/users/employees/ - создать сотрудника
    GET /api/users/employees/{id}/ - получить сотрудника
    PUT/PATCH /api/users/employees/{id}/ - обновить сотрудника
    DELETE /api/users/employees/{id}/ - удалить сотрудника
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Только менеджеры видят всех сотрудников"""
        if self.request.user.role == 'manager':
            return User.objects.filter(role='employee')
        return User.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer

    def perform_create(self, serializer):
        """При создании сотрудника автоматически устанавливаем роль employee"""
        serializer.save(role='employee')

    def destroy(self, request, *args, **kwargs):
        """Проверяем, что менеджер не может удалить самого себя"""
        employee = self.get_object()
        if employee.id == request.user.id:
            return Response(
                {"detail": "Вы не можете удалить самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить все задачи конкретного сотрудника"""
        employee = self.get_object()
        tasks = employee.tasks.all().order_by('-created_at')

        from tasks.serializers import TaskSerializer
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Получить/обновить информацию о текущем пользователе"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user