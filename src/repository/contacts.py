from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import and_, case, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


class ContactsRepository:
    """Рівень доступу до даних (DAL/Repository) для контактів."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, body: ContactCreate, user: User) -> Contact:
        contact = Contact(**body.model_dump(), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user: User,
        q: str | None = None,
        q_first_name: str | None = None,
        q_last_name: str | None = None,
        q_email: str | None = None,
    ) -> list[Contact]:
        stmt = select(Contact).where(Contact.user_id == user.id)

        filters = []

        # Загальний пошук по трьох полях (OR).
        if q:
            like = f"%{q}%"
            filters.append(
                or_(
                    Contact.first_name.ilike(like),
                    Contact.last_name.ilike(like),
                    Contact.email.ilike(like),
                )
            )

        if q_first_name:
            filters.append(Contact.first_name.ilike(f"%{q_first_name}%"))
        if q_last_name:
            filters.append(Contact.last_name.ilike(f"%{q_last_name}%"))
        if q_email:
            filters.append(Contact.email.ilike(f"%{q_email}%"))

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(skip).limit(limit).order_by(Contact.id)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
        contact = await self.get_by_id(contact_id, user)
        if contact is None:
            return None

        data = body.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_by_id(contact_id, user)
        if contact is None:
            return None
        await self.db.delete(contact)
        await self.db.commit()
        return contact

    async def upcoming_birthdays(self, *, days: int = 7, user: User) -> list[Contact]:
        """
        Повертає контакти з днями народження у найближчі N днів.

        Логіка:
        - рахуємо "наступний день народження" (у поточному році або в наступному)
        - фільтруємо по діапазону [сьогодні, сьогодні + days]
        """

        today = date.today()
        end_date = today + timedelta(days=days)

        # next_birthday = дата дня народження у поточному році
        next_birthday = func.make_date(
            extract("year", func.current_date()),
            extract("month", Contact.birthday),
            extract("day", Contact.birthday),
        )

        # якщо день народження цього року вже був — беремо наступний рік
        next_birthday = case(
            (next_birthday < func.current_date(), next_birthday + func.make_interval(years=1)),
            else_=next_birthday,
        )

        stmt = (
            select(Contact)
            .where(
                and_(
                    Contact.user_id == user.id,
                    next_birthday >= today,
                    next_birthday <= end_date,
                )
            )
            .order_by(next_birthday, Contact.last_name, Contact.first_name)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

