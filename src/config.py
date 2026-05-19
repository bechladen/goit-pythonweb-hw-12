def get_database_url() -> str:
    """
    Повертає рядок підключення до бази даних.

    Очікуємо змінну оточення DATABASE_URL (або значення з .env), наприклад:
    postgresql+asyncpg://postgres:postgres@localhost:5432/contacts_db
    """

    # Центральне місце для конфігурації — settings (.env)
    from src.settings import settings

    url = settings.DATABASE_URL

    # Нормалізація на випадок, якщо в оточенні вказали інший драйвер.
    # Для цього проєкту ми використовуємо async SQLAlchemy, тому очікуємо саме asyncpg.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

    return url

