from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Сотрудник'),
        ('manager', 'Руководитель'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    # phone_number убрали, потому что он не нужен для базовой версии

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_employee(self):
        return self.role == 'employee'