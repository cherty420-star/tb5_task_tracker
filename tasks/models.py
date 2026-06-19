from django.db import models
from django.conf import settings
from django.utils import timezone


class Status(models.Model):
    """Статус задачи"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class Priority(models.Model):
    """Приоритет задачи"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    level = models.IntegerField(default=1, verbose_name='Уровень')

    class Meta:
        verbose_name = 'Приоритет'
        verbose_name_plural = 'Приоритеты'

    def __str__(self):
        return self.name


class Task(models.Model):
    """Модель задачи"""
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Статус'
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Приоритет'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Исполнитель'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Создал'
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name='Родительская задача'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assignee']),
            models.Index(fields=['parent_task']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Проверка: просрочена ли задача"""
        if self.deadline and self.status and self.status.name != 'Завершена':
            return timezone.now() > self.deadline
        return False

    @property
    def has_active_subtasks(self):
        """Есть ли подзадачи в работе"""
        return self.subtasks.filter(
            status__name__in=['Новая', 'В работе']
        ).exists()