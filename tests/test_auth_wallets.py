import hashlib
import secrets
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import cli
from ledger_api.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LEDGER_DB_PATH", str(tmp_path / "test.sqlite3"))
    with TestClient(app) as client:
        yield client


def register_login(client, email):
    credentials = {"email": email, "password": secrets.token_urlsafe(24)}
    response = client.post("/auth/register", json={"name": "Test", **credentials})
    assert response.status_code == 201
    login = client.post("/auth/login", json=credentials)
    assert login.status_code == 200
    assert login.json()["expires_in"] == 1800
    return (
        response.json(),
        {"Authorization": "Bearer " + login.json()["token"]},
        credentials,
    )


def test_credentials_and_sessions(client, monkeypatch):
    user, headers, credentials = register_login(client, "  TEST@Example.org ")
    assert user["email"] == "test@example.org"
    assert set(user) == {"user_id", "name", "email", "role", "created_at"}
    assert user["role"] == "USER"
    assert client.get("/auth/me", headers=headers).json() == user
    body = {**credentials, "name": "New", "email": user["email"]}
    assert client.post("/auth/register", json=body).status_code == 409
    for extra in (
        {"role": "ADMIN"},
        {"user_id": str(uuid4())},
        {"password": "x" * 11},
        {"password": "x" * 129},
    ):
        assert client.post("/auth/register", json={**body, **extra}).status_code == 400
    failures = [
        client.post(
            "/auth/login", json={"email": email, "password": secrets.token_urlsafe(20)}
        )
        for email in (user["email"], "missing@example.org")
    ]
    assert all(r.status_code == 401 for r in failures)
    assert failures[0].json() == failures[1].json()
    auth = app.state.auth
    with auth.db.connection() as conn:
        assert (
            conn.execute("SELECT password_hash FROM users")
            .fetchone()[0]
            .startswith("$argon2id$")
        )
        stored = conn.execute("SELECT token_digest FROM auth_sessions").fetchone()[0]
        assert (
            stored == hashlib.sha256(headers["Authorization"][7:].encode()).hexdigest()
        )
    for invalid in (
        {},
        {"Authorization": "Basic 123"},
        {"Authorization": "Bearer unknown"},
    ):
        assert client.get("/auth/me", headers=invalid).status_code == 401
    second = client.post("/auth/login", json=credentials).json()["token"]
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401
    now = auth.clock.now()
    monkeypatch.setattr(auth.clock, "now", lambda: now + timedelta(minutes=30))
    assert (
        client.get(
            "/auth/me", headers={"Authorization": "Bearer " + second}
        ).status_code
        == 401
    )


def test_wallet_permissions_and_local_admin(client, monkeypatch):
    owner, headers, _ = register_login(client, "owner@example.org")
    other, foreign, _ = register_login(client, "reader@example.org")
    path = f"/users/{owner['user_id']}/wallets"
    assert client.post(path, json={"currency": "INR"}).status_code == 401
    assert (
        client.post(path, headers=foreign, json={"currency": "INR"}).status_code == 403
    )
    assert (
        client.post(path, headers=headers, json={"currency": "EUR"}).status_code == 400
    )
    assert client.get("/wallets/invalid", headers=headers).status_code == 400
    for currency in ("INR", "USD"):
        created = client.post(path, headers=headers, json={"currency": currency})
        assert created.status_code == 201
        assert created.json()["balance_minor"] == 0
    assert (
        client.post(path, headers=headers, json={"currency": "USD"}).status_code == 409
    )
    wallets = client.get("/users/me/wallets", headers=headers).json()
    assert {wallet["currency"] for wallet in wallets} == {"INR", "USD"}
    resource = "/wallets/" + wallets[0]["wallet_id"]
    assert client.get(resource, headers=headers).json() == wallets[0]
    hidden = client.get(resource, headers=foreign)
    assert hidden.status_code == 404
    assert (
        hidden.json() == client.get("/wallets/" + str(uuid4()), headers=foreign).json()
    )
    cli.main(["grant-admin", "--email", other["email"].upper()])
    assert client.get(resource, headers=foreign).json() == wallets[0]
    assert client.get("/users/me/wallets", headers=foreign).json() == []
    assert (
        client.post(path, headers=foreign, json={"currency": "USD"}).status_code == 403
    )
    password = secrets.token_urlsafe(24)
    monkeypatch.setattr(cli, "getpass", lambda _: password)
    cli.main(["create-admin", "--name", "Admin", "--email", "admin@example.org"])
    login = client.post(
        "/auth/login", json={"email": "admin@example.org", "password": password}
    )
    assert login.json()["role"] == "ADMIN"
    assert client.get("/app").status_code == 200
