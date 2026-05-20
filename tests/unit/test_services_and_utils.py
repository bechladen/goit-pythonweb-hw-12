from __future__ import annotations

import pytest
from fastapi import HTTPException

from src import config as config_module
from src.services import auth as auth_module
from src.services import cloudinary_upload as cloudinary_module
from src.services import email as email_module
from src.services import passwords as passwords_module


def test_hash_and_verify_password_roundtrip():
    hashed = passwords_module.hash_password("secret12")
    assert passwords_module.verify_password("secret12", hashed) is True
    assert passwords_module.verify_password("wrong", hashed) is False


def test_get_database_url_normalizes_driver(monkeypatch):
    monkeypatch.setattr(config_module.settings, "DATABASE_URL", "postgresql://u:p@h:5432/db")
    assert config_module.get_database_url().startswith("postgresql+asyncpg://")


def test_get_database_url_keeps_asyncpg(monkeypatch):
    monkeypatch.setattr(
        config_module.settings,
        "DATABASE_URL",
        "postgresql+asyncpg://u:p@h:5432/db",
    )
    assert config_module.get_database_url() == "postgresql+asyncpg://u:p@h:5432/db"


def test_upload_avatar_returns_none_when_not_configured(monkeypatch):
    monkeypatch.setattr(cloudinary_module.settings, "CLOUDINARY_NAME", None)
    monkeypatch.setattr(cloudinary_module.settings, "CLOUDINARY_API_KEY", None)
    monkeypatch.setattr(cloudinary_module.settings, "CLOUDINARY_API_SECRET", None)

    assert cloudinary_module.upload_avatar(file_obj=b"123", username="u") is None


@pytest.mark.asyncio
async def test_send_verification_email_is_noop_when_not_configured(monkeypatch):
    monkeypatch.setattr(email_module.settings, "MAIL_USERNAME", None)
    monkeypatch.setattr(email_module.settings, "MAIL_PASSWORD", None)
    monkeypatch.setattr(email_module.settings, "MAIL_FROM", None)
    monkeypatch.setattr(email_module.settings, "MAIL_PORT", None)
    monkeypatch.setattr(email_module.settings, "MAIL_SERVER", None)

    # should not raise even with empty settings
    await email_module.send_verification_email(email="u@example.com", username="u", base_url="http://x/")


def test_get_email_from_token_rejects_wrong_scope(monkeypatch):
    # create normal token and then replace decoder to return wrong scope
    def fake_decode(token, secret, algorithms):
        return {"sub": "u@example.com", "scope": "wrong"}

    monkeypatch.setattr(auth_module.jwt, "decode", fake_decode)

    with pytest.raises(HTTPException) as exc:
        auth_module.get_email_from_token("t")
    assert exc.value.status_code == 422


def test_create_email_token_and_parse_roundtrip(monkeypatch):
    # Use real encode/decode but set deterministic secret
    monkeypatch.setattr(auth_module.settings, "JWT_SECRET", "test-secret")
    token = auth_module.create_email_token(email="u@example.com")
    email = auth_module.get_email_from_token(token)
    assert email == "u@example.com"


@pytest.mark.asyncio
async def test_get_current_user_uses_cache(monkeypatch):
    class DummyDB:  # pragma: no cover
        pass

    async def fake_get_cached_user(username: str):
        from src.models import User

        return User(id=1, username=username, email="u@example.com", hashed_password="x")

    repo_mock = pytest.MonkeyPatch()
    monkeypatch.setattr(auth_module, "get_cached_user", fake_get_cached_user)
    monkeypatch.setattr(auth_module, "UsersRepository", lambda db: repo_mock)  # should not be used

    token = auth_module.create_access_token(subject="u")
    user = await auth_module.get_current_user(token=token, db=DummyDB())
    assert user.username == "u"

