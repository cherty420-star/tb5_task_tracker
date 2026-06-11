from django.core.management.base import BaseCommand
from tasks.models import Status, Priority


class Command(BaseCommand):
    help = 'Загружает начальные данные (статусы и приоритеты)'

    def handle(self, *args, **options):
        # Статусы
        statuses = ['Новая', 'В работе', 'На проверке', 'Завершена', 'Отменена']
        for status_name in statuses:
            Status.objects.get_or_create(name=status_name)

        # Приоритеты
        priorities = [
            {'name': 'Низкий', 'level': 1},
            {'name': 'Средний', 'level': 2},
            {'name': 'Высокий', 'level': 3},
            {'name': 'Критический', 'level': 4},
        ]
        for priority_data in priorities:
            Priority.objects.get_or_create(name=priority_data['name'], defaults={'level': priority_data['level']})

        self.stdout.write(self.style.SUCCESS('✅ Начальные данные успешно загружены'))