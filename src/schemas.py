from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UserResponse(UserBase):
    id: int
    avatar: str | None = None
    confirmed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactBase(BaseModel):
    """Спільні поля контакту."""

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=3, max_length=30)
    birthday: date
    extra: str | None = None


class ContactCreate(ContactBase):
    """Схема для створення контакту."""


class ContactUpdate(BaseModel):
    """
    Схема для оновлення контакту.

    Усі поля необовʼязкові, щоб можна було робити часткове оновлення.
    """

    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=3, max_length=30)
    birthday: date | None = None
    extra: str | None = None


class ContactResponse(ContactBase):
    """Схема відповіді (що повертаємо клієнту)."""

    id: int

    model_config = ConfigDict(from_attributes=True)

