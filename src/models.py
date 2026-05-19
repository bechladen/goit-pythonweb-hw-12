from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовий клас для ORM-моделей."""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="user", cascade="all, delete")


class Contact(Base):
    """Модель контакту."""

    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("email", "user_id", name="uq_contacts_email_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)

    birthday: Mapped[date] = mapped_column(Date, nullable=False)

    # Додаткові дані — довільний текст (необовʼязково)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship(back_populates="contacts")

