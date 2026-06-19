from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Сотрудник'),
        ('manager', 'Руководитель'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    # Новые поля
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    position = models.CharField(max_length=100, verbose_name='Должность')

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_employee(self):
        return self.role == 'employee'