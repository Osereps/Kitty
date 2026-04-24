# Kittygram

API для приложения учёта котов.

## Зависимости

- Django==3.2.3
- djangorestframework==3.12.4
- djangorestframework-simplejwt==4.8.0
- djoser==2.1.0
- django-filter==21.1
- drf-spectacular==0.26.0

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

## Локальный запуск

1. Клонировать репозиторий:
```bash
git clone https://github.com/your-repo/kittygram2.git
cd kittygram2
```

2. Создать и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Выполнить миграции:
```bash
python3 manage.py migrate
```

4. Создать суперпользователя (опционально):
```bash
python3 manage.py createsuperuser
```

5. Запустить проект:
```bash
python3 manage.py runserver
```

## Запуск через Docker

```bash
docker-compose up -d
```

## API эндпоинты

- `GET/POST /api/cats/` - список котов
- `GET/PUT/PATCH/DELETE /api/cats/{id}/` - детали кота
- `GET /api/users/` - список пользователей
- `GET/POST /api/achievements/` - достижения
- `GET/POST /api/vaccines/` - вакцины
- `GET/POST /api/cat-vaccinations/` - вакцинации котов
- `POST /api/auth/users/` - регистрация
- `POST /api/auth/jwt/create/` - получить токен
- `POST /api/auth/jwt/refresh/` - обновить токен

## Документация API

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/