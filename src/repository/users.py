from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.schemas import UserCreate


class UsersRepository:
    """Рівень доступу до даних (DAL/Repository) для користувачів."""

    def __init__(self, db: AsyncSession):
        """Створює репозиторій з інʼєкцією `AsyncSession`."""
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """Повертає користувача за email або `None`, якщо не знайдено."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Повертає користувача за username або `None`, якщо не знайдено."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def exists_by_email_or_username(self, *, email: str, username: str) -> bool:
        """Перевіряє, чи існує користувач з таким email або username."""
        stmt = select(User.id).where(or_(User.email == email, User.username == username)).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, body: UserCreate, hashed_password: str) -> User:
        """Створює користувача та повертає створений ORM-обʼєкт."""
        user = User(
            username=body.username,
            email=body.email,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirm_email(self, email: str) -> User | None:
        """Позначає email як підтверджений; повертає користувача або `None`."""
        user = await self.get_by_email(email)
        if user is None:
            return None
        user.confirmed = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self, *, user: User, avatar_url: str) -> User:
        """Оновлює URL аватара користувача та повертає оновлений обʼєкт."""
        user.avatar = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user

