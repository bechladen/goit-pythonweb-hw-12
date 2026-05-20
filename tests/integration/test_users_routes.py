import pytest

from tests.integration.utils import auth_headers, seed_user
from src.services.auth import create_access_token


@pytest.mark.asyncio
async def test_me_returns_current_user(client, db_session):
    user = await seed_user(
        db=db_session,
        username="me1",
        email="me1@example.com",
        password="secret12",
        confirmed=True,
    )
    token = create_access_token(subject=user.username)

    resp = client.get("/api/users/me", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["username"] == "me1"
    assert data["email"] == "me1@example.com"


def test_update_avatar_mocks_cloudinary(client, monkeypatch):
    def fake_upload_avatar(*, file_obj, username: str):
        return f"http://example.com/{username}.png"

    monkeypatch.setattr("src.api.users.upload_avatar", fake_upload_avatar)

    resp = client.patch("/api/users/avatar", files={"file": ("a.png", b"123", "image/png")})
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_update_avatar_success_with_auth(client, db_session, monkeypatch):
    def fake_upload_avatar(*, file_obj, username: str):
        return f"http://example.com/{username}.png"

    monkeypatch.setattr("src.api.users.upload_avatar", fake_upload_avatar)

    user = await seed_user(
        db=db_session,
        username="ava1",
        email="ava1@example.com",
        password="secret12",
        confirmed=True,
    )
    token = create_access_token(subject=user.username)

    resp = client.patch(
        "/api/users/avatar",
        headers=auth_headers(token),
        files={"file": ("a.png", b"123", "image/png")},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["avatar"] == "http://example.com/ava1.png"

