from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event

import pytest
from ledger_test_helpers import make_ledger_scenario

from ledger_api.db import SQLiteDatabase
from ledger_api.main import app

PATH = "/admin/reconciliation"


def test_permissions_and_clean_report(client):
    scenario = make_ledger_scenario(client)
    assert client.get(PATH).status_code == 401
    assert client.get(PATH, headers=scenario["sender_headers"]).status_code == 403
    response = client.get(PATH, headers=scenario["admin_headers"])
    assert response.status_code == 200
    report = response.json()
    assert report["overall_status"] == "PASS"
    assert report["checked_transactions"] == report["checked_wallets"] == 2
    assert report["checked_entries"] == 4
    assert report["generated_at"].endswith("Z")
    assert all(not value for key, value in report.items() if key.startswith("failing_"))


@pytest.mark.parametrize("mismatch", ["hash", "cached_balance", "unbalanced_entry"])
def test_corrupt_copy_reports_ids(client, db, tmp_path, monkeypatch, mismatch):
    scenario = make_ledger_scenario(client)
    copy = SQLiteDatabase(tmp_path / "copy.sqlite3")
    with db.connection() as source, copy.connection() as destination:
        source.backup(destination)
    monkeypatch.setattr(app.state.auth, "db", copy)
    wallet = scenario["sender"]
    entry = scenario["transfer"]["entries"][0]
    with copy.write_transaction() as conn:
        if mismatch == "cached_balance":
            conn.execute(
                "UPDATE wallets SET balance_minor = balance_minor + 1 WHERE wallet_id = ?",
                (wallet["wallet_id"],),
            )
        else:
            conn.execute("DROP TRIGGER ledger_entries_no_update")
            if mismatch == "hash":
                conn.execute(
                    "UPDATE ledger_entries SET entry_hash = ? WHERE entry_id = ?",
                    ("0" * 64, entry["entry_id"]),
                )
            else:
                conn.execute(
                    "UPDATE ledger_entries SET amount_minor = amount_minor + 1 WHERE entry_id = ?",
                    (entry["entry_id"],),
                )
    report = client.get(PATH, headers=scenario["admin_headers"]).json()
    assert report["overall_status"] == "FAIL"
    if mismatch == "cached_balance":
        assert report["failing_wallet_ids"] == [wallet["wallet_id"]]
        assert report["failing_currencies"] == [wallet["currency"]]
        assert report["failing_entry_ids"] == []
    else:
        assert report["failing_entry_ids"] == [entry["entry_id"]]
        if mismatch == "unbalanced_entry":
            assert report["failing_transaction_ids"] == [entry["transaction_id"]]
            assert report["failing_currencies"] == [entry["currency"]]


def test_transfer_commits_during_reconciliation(client, monkeypatch):
    scenario = make_ledger_scenario(client)
    snapshot_started = Event()
    transfer_finished = Event()
    db = app.state.auth.db
    connect = db.connection

    def after_first_read(sql):
        if sql == "SELECT * FROM wallets ORDER BY wallet_id":
            snapshot_started.set()
            transfer_finished.wait(timeout=10)

    @contextmanager
    def observed_connection():
        with connect() as conn:
            conn.set_trace_callback(after_first_read)
            yield conn

    monkeypatch.setattr(db, "connection", observed_connection)
    with ThreadPoolExecutor() as pool:
        pending = pool.submit(client.get, PATH, headers=scenario["admin_headers"])
        try:
            assert snapshot_started.wait(timeout=10)
            response = client.post(
                "/transfers",
                headers={**scenario["sender_headers"], "Idempotency-Key": "snapshot-transfer"},
                json={
                    "sender_wallet_id": scenario["sender"]["wallet_id"],
                    "recipient_wallet_id": scenario["receiver"]["wallet_id"],
                    "amount_minor": 100,
                },
            )
            assert response.status_code == 201
            assert not pending.done()
        finally:
            transfer_finished.set()
        before = pending.result().json()
    after = client.get(PATH, headers=scenario["admin_headers"]).json()
    assert before["overall_status"] == after["overall_status"] == "PASS"
    assert (before["checked_entries"], after["checked_entries"]) == (4, 6)
