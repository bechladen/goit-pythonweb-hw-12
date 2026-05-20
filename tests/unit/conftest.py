from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture()
def db_session_mock() -> AsyncMock:
    """
    Async mock of SQLAlchemy `AsyncSession`.

    We unit-test repository logic in isolation (no real DB).
    """

    return AsyncMock(spec=AsyncSession)

