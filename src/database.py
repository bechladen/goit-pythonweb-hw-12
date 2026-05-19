import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_database_url


class DatabaseSessionManager:
    """
    Менеджер сесій БД.

    - Створює асинхронний engine
    - Надає контекстний менеджер для AsyncSession
    - Гарантує rollback при помилках і коректне закриття сесії
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url, echo=False)
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncSession:
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self) -> None:
        await self._engine.dispose()


session_manager = DatabaseSessionManager(get_database_url())


async def get_db() -> AsyncSession:
    """Залежність FastAPI: видає сесію БД на час запиту."""
    async with session_manager.session() as session:
        yield session


async def init_db() -> None:
    """Створення таблиць у БД (спрощено, без міграцій)."""
    from src.models import Base  # локальний імпорт, щоб уникнути циклів

    async with session_manager._engine.begin() as conn:  # noqa: SLF001 (для навчального проєкту)
        await conn.run_sync(Base.metadata.create_all)

