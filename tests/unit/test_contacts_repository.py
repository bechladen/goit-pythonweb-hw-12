from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas import ContactCreate, ContactUpdate


@pytest.fixture()
def repo(db_session_mock) -> ContactsRepository:
    return ContactsRepository(db_session_mock)


@pytest.fixture()
def user() -> User:
    return User(id=1, username="u", email="u@example.com", hashed_password="x")


@pytest.mark.asyncio
async def test_create_contact_commits(repo, db_session_mock, user):
    body = ContactCreate(
        first_name="A",
        last_name="B",
        email="c@example.com",
        phone="123",
        birthday=date(2000, 1, 1),
        extra=None,
    )

    created = await repo.create(body, user)

    assert isinstance(created, Contact)
    assert created.user_id == user.id
    assert created.email == "c@example.com"
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_awaited_once()
    db_session_mock.refresh.assert_awaited_once_with(created)


@pytest.mark.asyncio
async def test_list_contacts_returns_scalars_all(repo, db_session_mock, user):
    expected = [
        Contact(
            id=1,
            first_name="A",
            last_name="B",
            email="c@example.com",
            phone="123",
            birthday=date(2000, 1, 1),
            extra=None,
            user_id=user.id,
        )
    ]
    result = MagicMock()
    result.scalars.return_value.all.return_value = expected
    db_session_mock.execute = AsyncMock(return_value=result)

    contacts = await repo.list(user=user, q="A")

    assert contacts == expected
    db_session_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none(repo, db_session_mock, user):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db_session_mock.execute = AsyncMock(return_value=result)

    contact = await repo.get_by_id(999, user)

    assert contact is None
    db_session_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_returns_none_when_missing(repo, user):
    repo.get_by_id = AsyncMock(return_value=None)

    updated = await repo.update(1, ContactUpdate(first_name="X"), user)

    assert updated is None


@pytest.mark.asyncio
async def test_update_applies_partial_fields(repo, db_session_mock, user):
    existing = Contact(
        id=1,
        first_name="A",
        last_name="B",
        email="c@example.com",
        phone="123",
        birthday=date(2000, 1, 1),
        extra=None,
        user_id=user.id,
    )
    repo.get_by_id = AsyncMock(return_value=existing)

    updated = await repo.update(1, ContactUpdate(first_name="NEW"), user)

    assert updated is existing
    assert existing.first_name == "NEW"
    db_session_mock.commit.assert_awaited_once()
    db_session_mock.refresh.assert_awaited_once_with(existing)


@pytest.mark.asyncio
async def test_delete_returns_none_when_missing(repo, user):
    repo.get_by_id = AsyncMock(return_value=None)

    deleted = await repo.delete(1, user)

    assert deleted is None


@pytest.mark.asyncio
async def test_delete_deletes_and_commits(repo, db_session_mock, user):
    existing = Contact(
        id=1,
        first_name="A",
        last_name="B",
        email="c@example.com",
        phone="123",
        birthday=date(2000, 1, 1),
        extra=None,
        user_id=user.id,
    )
    repo.get_by_id = AsyncMock(return_value=existing)

    deleted = await repo.delete(1, user)

    assert deleted is existing
    db_session_mock.delete.assert_awaited_once_with(existing)
    db_session_mock.commit.assert_awaited_once()

