from datetime import date

import pytest

from tests.integration.utils import auth_headers, seed_user
from src.services.auth import create_access_token


@pytest.mark.asyncio
async def test_contacts_crud_flow(client, db_session):
    user = await seed_user(
        db=db_session,
        username="john2",
        email="john2@example.com",
        password="secret12",
        confirmed=True,
    )
    token = create_access_token(subject=user.username)

    # create
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": "c1@example.com",
        "phone": "123",
        "birthday": str(date(2000, 1, 1)),
        "extra": None,
    }
    resp = client.post("/api/contacts/", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["email"] == "c1@example.com"
    contact_id = created["id"]

    # list
    resp = client.get("/api/contacts/", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)

    # get by id
    resp = client.get(f"/api/contacts/{contact_id}", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == contact_id

    # update
    resp = client.put(
        f"/api/contacts/{contact_id}",
        json={"first_name": "NEW"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["first_name"] == "NEW"

    # delete
    resp = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text

    # get after delete
    resp = client.get(f"/api/contacts/{contact_id}", headers=auth_headers(token))
    assert resp.status_code == 404, resp.text

