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

### 1) Підняти PostgreSQL

Рекомендовано через Docker Compose:

```bash
docker compose up -d
```

База буде доступна на `localhost:5432`.

### 2) Налаштувати змінні оточення

Створіть файл `.env` на основі `.env.example` і за потреби змініть `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/contacts_db
```

### 3) Встановити залежності (Poetry)

```bash
poetry lock
poetry install
```

### 4) Запустити API

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

## Ендпоінти

Базовий префікс: `/api`

### Contacts

- **Створити контакт**
  - `POST /api/contacts`

- **Список контактів (з пошуком та пагінацією)**
  - `GET /api/contacts?skip=0&limit=100&q=...&first_name=...&last_name=...&email=...`
  - `q` шукає одразу по **імені/прізвищу/email** (OR-логіка)

- **Отримати контакт**
  - `GET /api/contacts/{contact_id}`

- **Оновити контакт**
  - `PUT /api/contacts/{contact_id}`
  - У тілі можна передавати тільки ті поля, які треба змінити.

- **Видалити контакт**
  - `DELETE /api/contacts/{contact_id}`

- **Дні народження на найближчі N днів**
  - `GET /api/contacts/birthdays?days=7`

---

## Примітки

- Проєкт **асинхронний**: використовується `postgresql+asyncpg` і `AsyncSession`.
- Для простоти таблиці створюються автоматично на старті застосунку (`create_all`).
  - У реальних проєктах краще використовувати **міграції Alembic**.
