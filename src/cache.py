from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from redis.asyncio import Redis

from src.models import User
from src.settings import settings

_redis: Redis | None = None


def _get_redis() -> Redis | None:
    global _redis  # noqa: PLW0603
    if settings.REDIS_URL is None:
        return None
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis


def _user_cache_key(username: str) -> str:
    return f"user:{username}"


def _serialize_user(user: User) -> str:
    payload = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
        "created_at": user.created_at.isoformat() if isinstance(user.created_at, datetime) else None,
    }
    return json.dumps(payload)


def _deserialize_user(raw: str) -> User:
    data: dict[str, Any] = json.loads(raw)
    created_at = data.get("created_at")
    return User(
        id=data["id"],
        username=data["username"],
        email=data["email"],
        hashed_password="",
        avatar=data.get("avatar"),
        confirmed=bool(data.get("confirmed")),
        created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
    )


async def get_cached_user(username: str) -> User | None:
    redis = _get_redis()
    if redis is None:
        return None
    raw = await redis.get(_user_cache_key(username))
    if raw is None:
        return None
    return _deserialize_user(raw)


async def set_cached_user(user: User) -> None:
    redis = _get_redis()
    if redis is None:
        return
    await redis.set(_user_cache_key(user.username), _serialize_user(user), ex=settings.USER_CACHE_TTL_SECONDS)


async def invalidate_cached_user(username: str) -> None:
    redis = _get_redis()
    if redis is None:
        return
    await redis.delete(_user_cache_key(username))

