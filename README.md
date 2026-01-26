# Project Bot

Telegram SaaS-платформа для трейдерских скринеров с подписками и реферальной системой.

---

## 🧱 Архитектура (v1)

Проект построен по принципу разделения ответственности:
- **Боты** — только обработка Telegram-событий
- **Сервисы** — бизнес-логика
- **Storage** — работа с базой данных
- **DB** — PostgreSQL + Alembic

---

## 🤖 Боты

### Admin Bot
Функции:
- управление пользователями
- блокировка / разблокировка
- выдача и удаление подписок
- просмотр реферальной информации (v1)
- системные разделы (в разработке)

### User Bot
Функции:
- регистрация пользователя
- реферальные ссылки
- проверка подписки (скоро)
- доступ к скринерам (будет)

---

## 🧩 Сервисы

### UsersService
Отвечает за:
- создание пользователя
- блокировку / разблокировку
- учёт рефералов

### SubscriptionsService
Отвечает за:
- добавление подписки (+N дней)
- продление активной подписки
- удаление подписки
- проверку активности подписки

---

## 🗄 Storage

### PostgresUsersStorage
Единый интерфейс для работы с пользователями:
- `add`
- `get`
- `get_all`
- `update`
- `update_subscription`

---

## 🗃 База данных

- PostgreSQL
- Alembic используется для миграций
- Все изменения схемы БД проходят через Alembic

---

## 🔐 Переменные окружения (.env)

```env
ADMIN_BOT_TOKEN=
ADMIN_TELEGRAM_ID=

USER_BOT_TOKEN=
USER_BOT_USERNAME=

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

ENV=dev




____________________________________________


## Architecture

- Python 3.11
- aiogram 3.x
- PostgreSQL
- SQLAlchemy (async)
- Alembic (migrations)

### Core layers
- bots/
  - admin_bot
  - user_bot
- core/
  - db/
  - storage/
  - services/
- tools/
  - diag_contracts.py

### Key principles
- Services depend on Storage
- Bots depend on Services
- No direct DB access from bots
