from ledger_test_helpers import make_ledger_scenario
from test_wallet_operations_api import register_login


def test_transaction_details_for_participants(client):
    scenario = make_ledger_scenario(client)

    transaction = scenario["transfer"]
    path = f"/transactions/{transaction['transaction_id']}"

    for headers in (
        scenario["sender_headers"],
        scenario["receiver_headers"],
        scenario["admin_headers"],
    ):
        response = client.get(path, headers=headers)

        assert response.status_code == 200
        assert response.json() == transaction
        assert len(response.json()["entries"]) == 2


def test_transaction_details_require_participation(client):
    scenario = make_ledger_scenario(client)

    _, headers = register_login(
        client, "ledger-observer@example.org"
    )

    transaction_id = scenario["transfer"]["transaction_id"]

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_user_wallet_ledger_filter(client):
    scenario = make_ledger_scenario(client)

    wallet_id = scenario["sender"]["wallet_id"]

    response = client.get(
        "/ledger-entries",
        headers=scenario["sender_headers"],
        params={"wallet_id": wallet_id},
    )

    assert response.status_code == 200

    entries = response.json()["entries"]

    assert len(entries) == 2
    assert [entry["direction"] for entry in entries] == [
        "CREDIT",
        "DEBIT",
    ]

    transaction_response = client.get(
        "/ledger-entries",
        headers=scenario["sender_headers"],
        params={
            "wallet_id": wallet_id,
            "transaction_id": scenario["transfer"]["transaction_id"],
        },
    )

    assert transaction_response.status_code == 200
    assert len(transaction_response.json()["entries"]) == 1


def test_user_ledger_requires_wallet(client):
    scenario = make_ledger_scenario(client)

    response = client.get(
        "/ledger-entries",
        headers=scenario["sender_headers"],
    )

    assert response.status_code == 400


def test_admin_ledger_pagination(client):
    scenario = make_ledger_scenario(client)

    first = client.get(
        "/ledger-entries",
        headers=scenario["admin_headers"],
        params={"limit": 2, "offset": 0},
    )

    second = client.get(
        "/ledger-entries",
        headers=scenario["admin_headers"],
        params={"limit": 2, "offset": 2},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert [
        entry["entry_id"]
        for entry in first.json()["entries"]
    ] == [1, 2]

    assert [
        entry["entry_id"]
        for entry in second.json()["entries"]
    ] == [3, 4]

    assert first.json()["limit"] == 2
    assert second.json()["offset"] == 2


def test_invalid_ledger_pagination(client):
    scenario = make_ledger_scenario(client)

    response = client.get(
        "/ledger-entries",
        headers=scenario["admin_headers"],
        params={"limit": 101},
    )

    assert response.status_code == 400
    