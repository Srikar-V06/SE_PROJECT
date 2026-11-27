from ledger_test_helpers import make_ledger_scenario

from ledger_api.main import app
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.wallets import WalletRepository


def test_admin_reversal_and_replay(client):
    scenario = make_ledger_scenario(client)
    original = scenario["transfer"]

    path = f"/transactions/{original['transaction_id']}/reverse"

    headers = {
        **scenario["admin_headers"],
        "Idempotency-Key": "test-reversal-1",
    }

    response = client.post(path, headers=headers)

    assert response.status_code == 201

    result = response.json()

    assert result["type"] == "REVERSAL"
    assert result["reversal_of_transaction_id"] == original["transaction_id"]

    for old_entry, new_entry in zip(
        original["entries"], result["entries"], strict=True
    ):
        assert old_entry["account_id"] == new_entry["account_id"]
        assert old_entry["amount_minor"] == new_entry["amount_minor"]
        assert old_entry["direction"] != new_entry["direction"]

    replay = client.post(path, headers=headers)

    assert replay.status_code == 201
    assert replay.json() == result
    assert replay.headers["Idempotent-Replayed"] == "true"

    with app.state.auth.db.connection() as conn:
        wallets = WalletRepository(conn)

        assert wallets.get(
            scenario["sender"]["wallet_id"]
        )["balance_minor"] == 10000

        assert wallets.get(
            scenario["receiver"]["wallet_id"]
        )["balance_minor"] == 0

        ledger = LedgerEntryRepository(conn)

        stored = [
            dict(row)
            for row in ledger.get_for_transaction(
                original["transaction_id"]
            )
        ]

        assert stored == original["entries"]
        assert ledger.verify_chain().overall_status == "PASS"

        assert conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0] == 3


def test_reversal_business_rules(client):
    scenario = make_ledger_scenario(client)

    transaction_id = scenario["transfer"]["transaction_id"]
    path = f"/transactions/{transaction_id}/reverse"

    first = client.post(
        path,
        headers={
            **scenario["admin_headers"],
            "Idempotency-Key": "first-reversal",
        },
    )

    assert first.status_code == 201

    second = client.post(
        path,
        headers={
            **scenario["admin_headers"],
            "Idempotency-Key": "second-reversal",
        },
    )

    assert second.status_code == 409
    assert second.json()["code"] == "ALREADY_REVERSED"

    reversal_id = first.json()["transaction_id"]

    response = client.post(
        f"/transactions/{reversal_id}/reverse",
        headers={
            **scenario["admin_headers"],
            "Idempotency-Key": "reversal-reference",
        },
    )

    assert response.status_code == 409
    assert response.json()["code"] == "REVERSAL_OF_REVERSAL"


def test_reversal_overdraw_rejected(client):
    scenario = make_ledger_scenario(client)

    transaction_id = scenario["funding"]["transaction_id"]

    response = client.post(
        f"/transactions/{transaction_id}/reverse",
        headers={
            **scenario["admin_headers"],
            "Idempotency-Key": "funding-reversal-check",
        },
    )

    assert response.status_code == 422
    assert response.json()["code"] == "REVERSAL_OVERDRAW"

    with app.state.auth.db.connection() as conn:
        wallets = WalletRepository(conn)

        assert wallets.get(
            scenario["sender"]["wallet_id"]
        )["balance_minor"] == 7500

        assert conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0] == 2


def test_reversal_requires_admin(client):
    scenario = make_ledger_scenario(client)
    transaction_id = scenario["transfer"]["transaction_id"]

    response = client.post(
        f"/transactions/{transaction_id}/reverse",
        headers={
            **scenario["sender_headers"],
            "Idempotency-Key": "permission-check",
        },
    )

    assert response.status_code == 403