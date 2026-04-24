# 📋 Доска объявлений

Веб-приложение на Django — доска объявлений с регистрацией, авторизацией, поиском и категориями.

## 🛠 Технологии

- Python 3.11+
- Django 5.0
- PostgreSQL
- Bootstrap 5

## 📁 Структура проекта

```
bulletin_board/
├── bulletin_board/        # Настройки проекта
│   ├── settings.py
│   └── urls.py
├── accounts/              # Приложение: аккаунты
│   ├── models.py          # UserProfile (1:1 с User)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── ads/                   # Приложение: объявления
│   ├── models.py          # Ad, Category, Tag, Comment, Favorite
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── templates/             # Базовый шаблон
│   └── base.html
├── static/                # CSS и JS
├── fixtures/              # Начальные данные
│   └── initial_data.json
├── requirements.txt
└── .env.example
```

## ⚙️ Установка и запуск (Windows)

### 1. Клонируйте репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd bulletin_board
```

### 2. Создайте и активируйте виртуальное окружение

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте PostgreSQL

Создайте базу данных в PostgreSQL:
```sql
CREATE DATABASE bulletin_board;
```

### 5. Создайте файл .env

Скопируйте `.env.example` в `.env` и заполните:
```
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
DB_NAME=bulletin_board
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
```

### 6. Примените миграции

```bash
python manage.py migrate
```

### 7. Загрузите начальные данные

```bash
python manage.py loaddata fixtures/initial_data.json
```

### 8. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

### 9. Запустите сервер

```bash
python manage.py runserver
```

Откройте в браузере: http://127.0.0.1:8000/

## 🧪 Запуск тестов

```bash
python manage.py test
```

Запуск тестов конкретного приложения:
```bash
python manage.py test accounts
python manage.py test ads
```

## 👤 Модели и связи БД

| Модель | Связь | С чем |
|--------|-------|-------|
| UserProfile | 1:1 | User |
| Ad | N:1 | User, Category |
| Comment | N:1 | User, Ad |
| Favorite | N:N | User ↔ Ad |
| Tag | N:N | Ad ↔ Tag |

## 🔗 Маршруты

| URL | Описание |
|-----|----------|
| `/` | Главная, список объявлений + поиск |
| `/ad/<pk>/` | Детальная страница объявления |
| `/ad/create/` | Создать объявление |
| `/ad/<pk>/edit/` | Редактировать объявление |
| `/ad/<pk>/delete/` | Удалить объявление |
| `/ad/<pk>/favorite/` | Добавить/убрать из избранного |
| `/category/<slug>/` | Объявления по категории |
| `/favorites/` | Избранные объявления |
| `/my-ads/` | Мои объявления |
| `/accounts/register/` | Регистрация |
| `/accounts/login/` | Вход |
| `/accounts/logout/` | Выход |
| `/accounts/profile/` | Профиль пользователя |
| `/accounts/user/<username>/` | Объявления пользователя |
| `/admin/` | Панель администратора |

## 👥 Разделение задач

**Человек 1 (accounts + backend):**
- Модели: UserProfile
- Авторизация, регистрация, роли
- Django Admin
- Тесты: accounts/tests.py

**Человек 2 (ads + frontend):**
- Модели: Ad, Category, Tag, Comment, Favorite
- CRUD объявлений, поиск, фильтрация
- Все шаблоны + Bootstrap
- Тесты: ads/tests.py
