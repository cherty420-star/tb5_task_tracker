# Task Tracker API

Система для управления задачами сотрудников с разграничением прав доступа (руководитель/сотрудник).

## 🛠 Технологии

- Django 5.0.3
- Django REST Framework 3.15.1
- JWT аутентификация (SimpleJWT)
- SQLite (разработка)
- drf-spectacular (документация API)

## Быстрый старт

### 1. Клонирование и установка

```bash
git clone <your-repo-url>
cd tb5_task_tracker
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate (Windows)
pip install -r requirements.txt

2. Настройка БД и миграции
bash
python manage.py migrate
python manage.py load_initial_data  # загрузка статусов и приоритетов
python manage.py createsuperuser

3. Запуск сервера
bash
python manage.py runserver

API Эндпоинты

Метод	Эндпоинт	            Описание
POST	/api/users/register/	Регистрация
POST	/api/users/token/	    Получение JWT
GET	    /api/tasks/tasks/	    Список задач
POST	/api/tasks/tasks/	    Создать задачу
GET	    /api/tasks/tasks/{id}/	Детали задачи
PATCH	/api/tasks/tasks/{id}/	Обновить задачу
DELETE	/api/tasks/tasks/{id}/	Удалить задачу

Запуск тестов
bash
python manage.py test

Бизнес-ценность:
-Экономия времени: сокращение времени на учёт задач с 30 до 5 минут в день

-Прозрачность: руководитель видит загрузку каждого сотрудника

-Контроль: автоматическое назначение задач и отслеживание статусов

Роли:
-Руководитель (manager): видит и управляет всеми задачами

-Сотрудник (employee): видит только свои задачи

Документация API
После запуска сервера доступны:

Swagger UI: http://localhost:8000/api/schema/swagger/

ReDoc: http://localhost:8000/api/schema/redoc/

Админка: http://localhost:8000/admin/

## Скриншоты

### Swagger UI документация
![Swagger UI](screenshots/swagger_screenshot.png)

### Админка Django
![Django Admin](screenshots/admin_screenshot.png)

### Результаты тестирования
![Tests](screenshots/tests_screenshot.png)

## Покрытие тестами
![Coverage](screenshots/tests_screenshot2.png)