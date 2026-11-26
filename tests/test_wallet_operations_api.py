"""API integration coverage for idempotent funding and transfers."""

from concurrent.futures import ThreadPoolExecutor
from secrets import token_urlsafe
from threading import Barrier

from ledger_api.main import app
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.wallets import WalletRepository


def register_login(client, email):
    credentials = {"email": email, "password": token_urlsafe(24)}
    response = client.post(
        "/auth/register", json={"name": "API Test User", **credentials}
    )
    assert response.status_code == 201
    login = client.post("/auth/login", json=credentials)
    assert login.status_code == 200
    return response.json(), {"Authorization": f"Bearer {login.json()['token']}"}


def create_wallet(client, user, headers, currency="INR"):
    response = client.post(
        f"/users/{user['user_id']}/wallets",
        headers=headers,
        json={"currency": currency},
    )
    assert response.status_code == 201
    return response.json()


def promote_admin(user_id):
    with app.state.auth.db.write_transaction() as conn:
        conn.execute("UPDATE users SET role = 'ADMIN' WHERE user_id = ?", (user_id,))


def test_admin_funding_posts_and_replays_transaction(client):
    owner, owner_headers = register_login(client, "funding-owner@example.org")
    admin, admin_headers = register_login(client, "funding-admin@example.org")
    wallet = create_wallet(client, owner, owner_headers)
    path = f"/wallets/{wallet['wallet_id']}/fund"
    request = {"amount_minor": 12_500, "description": "test funding"}
    key_headers = {"Idempotency-Key": "funding-request-1"}

    forbidden = client.post(
        path, headers={**owner_headers, **key_headers}, json=request
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "FORBIDDEN"

    promote_admin(admin["user_id"])
    first = client.post(
        path, headers={**admin_headers, **key_headers}, json=request
    )
    replay = client.post(
        path, headers={**admin_headers, **key_headers}, json=request
    )
    conflict = client.post(
        path,
        headers={**admin_headers, **key_headers},
        json={"amount_minor": 12_501, "description": "test funding"},
    )

    assert first.status_code == 201
    assert first.json()["type"] == "FUNDING"
    assert [entry["direction"] for entry in first.json()["entries"]] == [
        "DEBIT",
        "CREDIT",
    ]
    assert replay.status_code == 201
    assert replay.json() == first.json()
    assert replay.headers["Idempotent-Replayed"] == "true"
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "IDEMPOTENCY_KEY_REUSED"

    with app.state.auth.db.connection() as conn:
        assert WalletRepository(conn).get(wallet["wallet_id"])["balance_minor"] == 12_500
        assert conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()[0] == 1
        assert LedgerEntryRepository(conn).verify_chain().overall_status == "PASS"


def test_transfer_permissions_validation_and_concurrent_idempotent_replay(client):
    sender_user, sender_headers = register_login(
        client, "transfer-sender@example.org"
    )
    recipient_user, recipient_headers = register_login(
        client, "transfer-recipient@example.org"
    )
    admin, admin_headers = register_login(client, "transfer-admin@example.org")

    sender = create_wallet(client, sender_user, sender_headers)
    recipient = create_wallet(client, recipient_user, recipient_headers)
    recipient_usd = create_wallet(client, recipient_user, recipient_headers, "USD")

    promote_admin(admin["user_id"])
    funding = client.post(
        f"/wallets/{sender['wallet_id']}/fund",
        headers={**admin_headers, "Idempotency-Key": "transfer-test-fund"},
        json={"amount_minor": 10_000},
    )
    assert funding.status_code == 201

    foreign_sender = client.post(
        "/transfers",
        headers={**recipient_headers, "Idempotency-Key": "foreign-sender"},
        json={
            "sender_wallet_id": sender["wallet_id"],
            "recipient_wallet_id": recipient["wallet_id"],
            "amount_minor": 100,
        },
    )
    assert foreign_sender.status_code == 404

    self_transfer = client.post(
        "/transfers",
        headers={**sender_headers, "Idempotency-Key": "self-transfer"},
        json={
            "sender_wallet_id": sender["wallet_id"],
            "recipient_wallet_id": sender["wallet_id"],
            "amount_minor": 100,
        },
    )
    assert self_transfer.status_code == 400

    currency_mismatch = client.post(
        "/transfers",
        headers={**sender_headers, "Idempotency-Key": "currency-mismatch"},
        json={
            "sender_wallet_id": sender["wallet_id"],
            "recipient_wallet_id": recipient_usd["wallet_id"],
            "amount_minor": 100,
        },
    )
    assert currency_mismatch.status_code == 422
    assert currency_mismatch.json()["code"] == "CURRENCY_MISMATCH"

    insufficient = client.post(
        "/transfers",
        headers={**sender_headers, "Idempotency-Key": "insufficient-funds"},
        json={
            "sender_wallet_id": sender["wallet_id"],
            "recipient_wallet_id": recipient["wallet_id"],
            "amount_minor": 10_001,
        },
    )
    assert insufficient.status_code == 422
    assert insufficient.json()["code"] == "INSUFFICIENT_FUNDS"

    start = Barrier(2)
    request_data = {
        "sender_wallet_id": sender["wallet_id"],
        "recipient_wallet_id": recipient["wallet_id"],
        "amount_minor": 2_500,
        "description": "test transfer",
    }
    headers = {**sender_headers, "Idempotency-Key": "concurrent-transfer-1"}

    def send_transfer():
        start.wait(timeout=5)
        return client.post("/transfers", headers=headers, json=request_data)

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: send_transfer(), range(2)))

    assert [response.status_code for response in responses] == [201, 201]
    assert responses[0].json() == responses[1].json()
    assert sorted(
        response.headers.get("Idempotent-Replayed") == "true"
        for response in responses
    ) == [False, True]
    assert responses[0].json()["type"] == "TRANSFER"
    assert [entry["direction"] for entry in responses[0].json()["entries"]] == [
        "DEBIT",
        "CREDIT",
    ]

    with app.state.auth.db.connection() as conn:
        wallets = WalletRepository(conn)
        assert wallets.get(sender["wallet_id"])["balance_minor"] == 7_500
        assert wallets.get(recipient["wallet_id"])["balance_minor"] == 2_500
        assert conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0] == 4
        assert LedgerEntryRepository(conn).verify_chain().overall_status == "PASS"
