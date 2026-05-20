from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models import User
from src.repository.users import UsersRepository
from src.schemas import UserCreate


@pytest.fixture()
def repo(db_session_mock) -> UsersRepository:
    return UsersRepository(db_session_mock)


@pytest.mark.asyncio
async def test_get_by_email_returns_user(repo, db_session_mock):
    expected = User(id=1, username="u", email="u@example.com", hashed_password="x")
    result = MagicMock()
    result.scalar_one_or_none.return_value = expected
    db_session_mock.execute = AsyncMock(return_value=result)

    user = await repo.get_by_email("u@example.com")

    assert user is expected
    db_session_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_username_returns_none(repo, db_session_mock):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db_session_mock.execute = AsyncMock(return_value=result)

    user = await repo.get_by_username("missing")

    assert user is None
    db_session_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_exists_by_email_or_username_true(repo, db_session_mock):
    result = MagicMock()
    result.scalar_one_or_none.return_value = 123
    db_session_mock.execute = AsyncMock(return_value=result)

    exists = await repo.exists_by_email_or_username(email="e@example.com", username="u")

    assert exists is True
    db_session_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_commits_and_refreshes(repo, db_session_mock):
    body = UserCreate(username="john", email="john@example.com", password="secret12")

    created = await repo.create(body, hashed_password="hashed")

    assert isinstance(created, User)
    assert created.username == "john"
    assert created.email == "john@example.com"
    assert created.hashed_password == "hashed"

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_awaited_once()
    db_session_mock.refresh.assert_awaited_once_with(created)


@pytest.mark.asyncio
async def test_confirm_email_updates_user(repo, db_session_mock):
    existing = User(id=1, username="u", email="u@example.com", hashed_password="x", confirmed=False)

    repo.get_by_email = AsyncMock(return_value=existing)

    updated = await repo.confirm_email("u@example.com")

    assert updated is existing
    assert existing.confirmed is True
    db_session_mock.commit.assert_awaited_once()
    db_session_mock.refresh.assert_awaited_once_with(existing)


@pytest.mark.asyncio
async def test_update_avatar_updates_and_persists(repo, db_session_mock):
    existing = User(id=1, username="u", email="u@example.com", hashed_password="x")

    updated = await repo.update_avatar(user=existing, avatar_url="http://example.com/a.png")

    assert updated is existing
    assert existing.avatar == "http://example.com/a.png"
    db_session_mock.commit.assert_awaited_once()
    db_session_mock.refresh.assert_awaited_once_with(existing)

