# Kittygram

API для приложения учёта котов с системой вакцинаций и напоминаний.

## Зависимости

- Django==3.2.3
- djangorestframework==3.12.4
- djangorestframework-simplejwt==4.8.0
- djoser==2.1.0
- django-filter==2.4.0
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

4. Создать суперпользователя (для управления справочником вакцин):
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

Миграции применяются автоматически при старте контейнера.

## API эндпоинты

### Аутентификация

| Метод | URL | Описание |
|---|---|---|
| POST | `/auth/users/` | Регистрация |
| POST | `/auth/jwt/create/` | Получить токен |
| POST | `/auth/jwt/refresh/` | Обновить токен |

### Коты

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET, POST | `/cats/` | Список/создание котов | Все / Авторизованные |
| GET, PUT, DELETE | `/cats/{id}/` | Детали кота | Все / Владелец |

Фильтры: `color`, `owner`. Поиск: `name`. Сортировка: `name`, `birth_year`.

### Пользователи

| Метод | URL | Описание |
|---|---|---|
| GET | `/users/` | Список пользователей (только чтение) |

### Достижения

| Метод | URL | Описание |
|---|---|---|
| GET, POST | `/achievements/` | Список/создание достижений |

### Вакцины (справочник)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/vaccines/` | Список вакцин | Все |
| POST, PUT, DELETE | `/vaccines/`, `/vaccines/{id}/` | Управление вакцинами | Только админ |

### Вакцинации котов

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET, POST | `/cat-vaccinations/` | Список/создание вакцинаций | Все / Владелец кота |
| GET, PUT, DELETE | `/cat-vaccinations/{id}/` | Детали/редактирование | Владелец кота |
| GET | `/cat-vaccinations/expired/` | Просроченные вакцинации | Авторизованные |
| GET | `/cat-vaccinations/upcoming/?days=7` | Скоро нужные (по умолчанию 7 дней) | Авторизованные |
| GET | `/cat-vaccinations/due/` | Все просроченные (overdue) | Авторизованные |
| POST | `/cat-vaccinations/{id}/complete/` | Отметить вакцинацию выполненной | Владелец кота |
| POST | `/cat-vaccinations/{id}/remind/` | Создать напоминание о вакцинации | Владелец кота |

Фильтры: `cat`, `vaccine`, `date`, `status` (expired/pending/completed). Сортировка: `date`, `next_date`.

### Напоминания

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET, POST | `/reminders/` | Список/создание напоминаний | Владелец кота |
| GET, PUT, DELETE | `/reminders/{id}/` | Детали/редактирование напоминания | Владелец кота |

Фильтры: `cat`. Сортировка: `created_at`.

## Документация API

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## Валидации

| Правило | Где проверяется | Сообщение |
|---|---|---|
| `next_date > date` | CatVaccinationSerializer | Дата следующей вакцинации должна быть позже даты текущей |
| Без дублей (1 вакцина в день на кота) | CatVaccinationSerializer | Уже существует запись о вакцинации этим препаратом |
| Имя кота ≥ 2 символа | CatSerializer | Имя кота должно содержать минимум 2 символа |
| Название вакцины ≥ 3 символа | VaccineSerializer | Название вакцины должно содержать минимум 3 символа |

## Статусы вакцинаций

- `pending` — активная вакцинация, срок ещё не истёк
- `expired` — просроченная вакцинация (`next_date < сегодня` и не выполнена)
- `completed` — вакцинация отмечена как выполненная
