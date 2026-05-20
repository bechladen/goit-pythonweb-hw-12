## Contacts REST API (FastAPI + SQLAlchemy + PostgreSQL)

**REST API для зберігання та управління контактами**

### Можливості

- **CRUD** для контактів
  - створити контакт
  - отримати список контактів
  - отримати контакт за `id`
  - оновити контакт
  - видалити контакт
- **Пошук** контактів за `first_name`, `last_name`, `email` (query-параметри)
- **Найближчі дні народження**: список контактів, у яких день народження на найближчі \(N\) днів (за замовчуванням 7)
- **Auth (JWT)**: реєстрація / логін / підтвердження email
- **Reset password**: запит на скидання + підтвердження токеном
- **Ролі**: `user` / `admin`
  - лише **admin** може оновлювати аватар
- **Redis кеш**: кешування поточного користувача в `get_current_user`
- **Swagger / OpenAPI** документація автоматично

### Дані контакту

- **Імʼя** (`first_name`)
- **Прізвище** (`last_name`)
- **Email** (`email`, унікальний)
- **Телефон** (`phone`)
- **День народження** (`birthday`, формат `YYYY-MM-DD`)
- **Додаткові дані** (`extra`, необовʼязково)

---

## Запуск

### Варіант A: Docker Compose (рекомендовано)

1) Створіть `.env` на основі `.env.example`.

Мінімально потрібні значення для Docker:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/contacts_db
AUTO_CREATE_TABLES=False

REDIS_URL=redis://redis:6379/0
USER_CACHE_TTL_SECONDS=300

JWT_SECRET=change_me_now
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600
```

2) Запустіть сервіси:

```bash
docker compose up --build -d
```

3) Застосуйте міграції:

```bash
docker compose exec api alembic upgrade head
```

4) Відкрийте документацію:

- Swagger UI: `http://localhost:8000/docs`

---

### Варіант B: локально (Poetry)

1) Створіть `.env` на основі `.env.example` і задайте мінімум:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/contacts_db
JWT_SECRET=change_me_now
```

2) Встановіть залежності:

```bash
poetry lock
poetry install
```

3) Запустіть API:

Варіант A (FastAPI CLI):

```bash
poetry run fastapi dev main.py
```

Варіант B (через Uvicorn):

```bash
poetry run uvicorn main:app --reload
```

---

## Документація

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Тести та покриття

Запуск усіх тестів:

```bash
poetry run pytest
```

Покриття (ціль: **>= 75%**):

```bash
poetry run pytest --cov=src --cov-report=term-missing
```

HTML-звіт:

```bash
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Sphinx документація коду

```bash
poetry run sphinx-build -b html docs docs/_build/html
open docs/_build/html/index.html
```

---

## Примітки

- Проєкт **асинхронний**: використовується `postgresql+asyncpg` і `AsyncSession`.
- Для керування схемою БД використовується **Alembic**.
- `AUTO_CREATE_TABLES=True` — навчальний режим (створює таблиці через `create_all()` на старті).
  - Для нормальної роботи міграцій встановіть `AUTO_CREATE_TABLES=False`.
