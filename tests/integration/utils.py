from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.services.passwords import hash_password


async def seed_user(
    *,
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    confirmed: bool = True,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        confirmed=confirmed,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

