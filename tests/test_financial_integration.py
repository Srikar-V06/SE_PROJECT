"""Phase 4 API checks against an isolated migrated SQLite database."""

from datetime import datetime
from secrets import token_urlsafe

import pytest
from test_wallet_operations_api import create_wallet, promote_admin, register_login

from ledger_api.main import app
from ledger_api.repositories.idempotency import IdempotencyRepository


def posted_state(db):
    """Capture balances and posting counts across independent requests."""
    with db.connection() as conn:
        return (
            dict(conn.execute("SELECT wallet_id, balance_minor FROM wallets")),
            conn.execute("SELECT count(*) FROM transactions").fetchone()[0],
            conn.execute("SELECT count(*) FROM ledger_entries").fetchone()[0],
            conn.execute("SELECT count(*) FROM idempotency_keys").fetchone()[0],
        )


def test_key_replay_and_expiry_across_login_sessions(
    client, db, fake_clock, monkeypatch
):
    monkeypatch.setattr(app.state.auth, "clock", fake_clock)
    credentials = {"email": "retention@example.org", "password": token_urlsafe(24)}
    registered = client.post(
        "/auth/register", json={"name": "Retention", **credentials}
    )
    assert registered.status_code == 201
    user = registered.json()
    promote_admin(user["user_id"])

    def login():
        response = client.post("/auth/login", json=credentials)
        assert response.status_code == 200
        return {"Authorization": "Bearer " + response.json()["token"]}

    headers = login()
    wallet = create_wallet(client, user, headers)
    wallet_id = wallet["wallet_id"]

    def fund(headers):
        return client.post(
            f"/wallets/{wallet_id}/fund",
            headers={**headers, "Idempotency-Key": "same-funding"},
            json={"amount_minor": 100},
        )

    first = fund(headers)
    assert first.status_code == 201
    with db.connection() as conn:
        key = IdempotencyRepository(conn).get(user["user_id"], "same-funding")
        expires = datetime.fromisoformat(key["expires_at"])
    lifetime = (expires - fake_clock.now()).total_seconds()
    assert lifetime >= 24 * 3600
    fake_clock.advance(lifetime - 1)
    assert fund(headers).status_code == 401
    headers = login()
    replay = fund(headers)
    assert replay.status_code == 201
    assert replay.headers["Idempotent-Replayed"] == "true"
    assert replay.json() == first.json()
    assert posted_state(db) == ({wallet_id: 100}, 1, 2, 1)
    fake_clock.advance(1)
    fresh = fund(headers)
    assert fresh.status_code == 201
    assert "Idempotent-Replayed" not in fresh.headers
    assert fresh.json()["transaction_id"] != first.json()["transaction_id"]
    assert posted_state(db) == ({wallet_id: 200}, 2, 4, 1)


def test_two_users_can_use_the_same_key(client, db):
    users = [register_login(client, f"scope-{i}@example.org") for i in range(2)]
    wallet = create_wallet(client, *users[0])
    wallet_id = wallet["wallet_id"]
    transactions = set()
    for user, headers in users:
        promote_admin(user["user_id"])
        result = client.post(
            f"/wallets/{wallet_id}/fund",
            headers={**headers, "Idempotency-Key": "shared"},
            json={"amount_minor": 25},
        )
        assert result.status_code == 201
        assert "Idempotent-Replayed" not in result.headers
        transactions.add(result.json()["transaction_id"])
    assert len(transactions) == 2
    assert posted_state(db) == ({wallet_id: 50}, 2, 4, 2)


def test_transfer_rolls_back_if_saving_key_fails(client, db, monkeypatch):
    sender, headers = register_login(client, "rollback@example.org")
    promote_admin(sender["user_id"])
    source = create_wallet(client, sender, headers)["wallet_id"]
    recipient = create_wallet(client, *register_login(client, "receiver@example.org"))[
        "wallet_id"
    ]
    funded = client.post(
        f"/wallets/{source}/fund",
        headers={**headers, "Idempotency-Key": "setup"},
        json={"amount_minor": 100},
    )
    assert funded.status_code == 201
    before = posted_state(db)
    request = {
        "headers": {**headers, "Idempotency-Key": "retry"},
        "json": {
            "sender_wallet_id": source,
            "recipient_wallet_id": recipient,
            "amount_minor": 40,
        },
    }

    def fail_save(self, **kwargs):
        assert kwargs["transaction_id"]
        raise RuntimeError("injected failure saving replay record")

    with monkeypatch.context() as patch:
        patch.setattr(IdempotencyRepository, "save", fail_save)
        with pytest.raises(RuntimeError, match="injected failure saving replay record"):
            client.post("/transfers", **request)
    assert posted_state(db) == before
    retry = client.post("/transfers", **request)
    assert retry.status_code == 201
    assert "Idempotent-Replayed" not in retry.headers
    assert posted_state(db) == ({source: 60, recipient: 40}, 2, 4, 2)


def test_invalid_financial_requests_leave_no_writes(client, db):
    user, headers = register_login(client, "validation@example.org")
    promote_admin(user["user_id"])
    wallet = create_wallet(client, user, headers)["wallet_id"]
    before = posted_state(db)
    body = {"amount_minor": 50}
    keyed = {**headers, "Idempotency-Key": "valid"}
    path = f"/wallets/{wallet}/fund"
    cases = [
        (path, headers, body),
        (path, {**headers, "Idempotency-Key": ""}, body),
        (path, {**headers, "Idempotency-Key": "k" * 129}, body),
        ("/wallets/invalid/fund", keyed, body),
        ("/transactions/invalid/reverse", keyed, {}),
        (
            "/transfers",
            keyed,
            {**body, "sender_wallet_id": wallet, "recipient_wallet_id": "invalid"},
        ),
    ]
    for url, request_headers, payload in cases:
        response = client.post(url, headers=request_headers, json=payload)
        assert response.status_code == 400, (url, response.text)
        assert response.json()["code"] == "VALIDATION_ERROR"
        assert posted_state(db) == before
