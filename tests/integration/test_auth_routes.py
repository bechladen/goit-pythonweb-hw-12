import pytest

from tests.integration.utils import auth_headers, seed_user


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    await seed_user(
        db=db_session,
        username="john",
        email="john@example.com",
        password="secret12",
        confirmed=True,
    )

    resp = client.post("/api/auth/login", json={"username": "john", "password": "secret12"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_denied_when_not_confirmed(client, db_session):
    await seed_user(
        db=db_session,
        username="kate",
        email="kate@example.com",
        password="secret12",
        confirmed=False,
    )

    resp = client.post("/api/auth/login", json={"username": "kate", "password": "secret12"})
    assert resp.status_code == 401, resp.text
    assert resp.json()["detail"] == "Email is not confirmed"


@pytest.mark.asyncio
async def test_request_email_always_ok(client, db_session):
    await seed_user(
        db=db_session,
        username="eva",
        email="eva@example.com",
        password="secret12",
        confirmed=False,
    )

    resp = client.post("/api/auth/request_email", json={"email": "eva@example.com"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["message"] == "Check your email for verification link"


@pytest.mark.asyncio
async def test_password_reset_flow(client, db_session):
    user = await seed_user(
        db=db_session,
        username="reset1",
        email="reset1@example.com",
        password="secret12",
        confirmed=True,
    )

    resp = client.post("/api/auth/request_password_reset", json={"email": user.email})
    assert resp.status_code == 200, resp.text

    from src.services.auth import create_password_reset_token

    token = create_password_reset_token(email=user.email)
    resp = client.post(
        "/api/auth/confirm_password_reset",
        json={"token": token, "new_password": "newsecret12"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["message"] == "Password updated"

