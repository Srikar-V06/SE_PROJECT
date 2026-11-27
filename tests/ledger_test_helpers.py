"""Create synthetic transactions for ledger API tests."""

from test_wallet_operations_api import (
    create_wallet,
    promote_admin,
    register_login,
)


def make_ledger_scenario(client):
    sender_user, sender_headers = register_login(
        client, "ledger-sender@example.org"
    )

    receiver_user, receiver_headers = register_login(
        client, "ledger-receiver@example.org"
    )

    admin, admin_headers = register_login(
        client, "ledger-admin@example.org"
    )

    promote_admin(admin["user_id"])

    sender = create_wallet(client, sender_user, sender_headers)
    receiver = create_wallet(client, receiver_user, receiver_headers)

    funding = client.post(
        f"/wallets/{sender['wallet_id']}/fund",
        headers={
            **admin_headers,
            "Idempotency-Key": "ledger-test-funding",
        },
        json={"amount_minor": 10000},
    )

    assert funding.status_code == 201

    transfer = client.post(
        "/transfers",
        headers={
            **sender_headers,
            "Idempotency-Key": "ledger-test-transfer",
        },
        json={
            "sender_wallet_id": sender["wallet_id"],
            "recipient_wallet_id": receiver["wallet_id"],
            "amount_minor": 2500,
        },
    )

    assert transfer.status_code == 201

    return {
        "sender": sender,
        "receiver": receiver,
        "sender_headers": sender_headers,
        "receiver_headers": receiver_headers,
        "admin_headers": admin_headers,
        "funding": funding.json(),
        "transfer": transfer.json(),
    }