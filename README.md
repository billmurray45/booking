# Hotel Booking System

Система бронирования отелей с REST API на Django REST Framework.

## Технологии

- **Django 6.0** + **Django REST Framework 3.16.1**
- **PostgreSQL 16**
- **JWT Authentication**
- **Docker** + **Docker Compose**
- **Python 3.12**

## Функциональность

- Регистрация и аутентификация пользователей (JWT)
- Управление комнатами (CRUD)
- Бронирование комнат
- Проверка доступности комнат на даты
- Swagger документация API

## Быстрый старт (Docker)

### 1. Настройка окружения

Создайте файл `.env`:

```bash
cp .env.example .env
```

Минимальная конфигурация:

```env
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True

DB_NAME=booking_db
DB_USER=booking_admin
DB_PASSWORD=your_password
DB_HOST=postgres
DB_PORT=5432

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

### 2. Запуск

```bash
docker compose up -d
```

При первом запуске автоматически:
- Установятся зависимости
- Применятся миграции
- Создастся суперпользователь (admin/admin)

### 3. Доступ к приложению

- **API**: http://localhost:8000
- **Swagger документация**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

### 4. Остановка

```bash
docker compose down
```

## Локальный запуск (без Docker)

### 1. Установка зависимостей

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Создание базы данных

```sql
CREATE DATABASE booking_db;
CREATE USER booking_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE booking_db TO booking_user;
```

### 3. Настройка .env

```env
DB_HOST=localhost
DB_PORT=5432
```

### 4. Миграции и запуск

```bash
cd app
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

## Основные API эндпоинты

### Аутентификация
- `POST /api/v1/users/register/` - Регистрация
- `POST /api/v1/users/login/` - Вход (получение JWT токенов)
- `POST /api/v1/users/logout/` - Выход

### Комнаты
- `GET /api/v1/rooms/` - Список комнат
- `GET /api/v1/rooms/available/` - Доступные комнаты на даты
- `POST /api/v1/rooms/create/` - Создать комнату (admin)

### Бронирования
- `GET /api/v1/bookings/` - Список бронирований
- `POST /api/v1/bookings/create/` - Создать бронирование
- `PATCH /api/v1/bookings/{id}/update/` - Изменить даты
- `DELETE /api/v1/bookings/{id}/cancel/` - Отменить

Полная документация: http://localhost:8000/api/docs/

## Примеры использования

### 1. Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "email": "user@example.com",
    "password": "pass123",
    "password2": "pass123"
  }'
```

### 2. Вход

```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "password": "pass123"
  }'
```

### 3. Создание бронирования

```bash
curl -X POST http://localhost:8000/api/v1/bookings/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "check_in": "2025-12-28",
    "check_out": "2025-12-30"
  }'
```


## Логирование

Логи сохраняются в `logs/`:
- `logs/logs.txt` - основные логи
- `logs/errors.txt` - ошибки

Логируются все важные события (регистрация, вход, бронирования, отмены).
