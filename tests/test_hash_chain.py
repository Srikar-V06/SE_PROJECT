import sqlite3

import pytest

from ledger_api.ledger.hash_chain import (
    GENESIS_HASH,
    compute_entry_hash,
)
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository


def test_genesis_hash():
    assert GENESIS_HASH == "0" * 64


def test_known_entry_hash():
    result = compute_entry_hash(
        GENESIS_HASH,
        "T-1",
        "ACC-A",
        "DEBIT",
        500,
        "INR",
        "2026-11-20T10:00:00Z",
        1,
    )

    expected = (
        "4f073952144f327012741c8a0eaf65f29"
        "a48b57dbb9564a2b005fc5a5cb3bb2e"
    )

    assert result == expected


@pytest.fixture
def sample_transaction(db, fake_ids):
    transaction_id = fake_ids.new_id()
    timestamp = "2026-01-01T00:00:00Z"

    with db.write_transaction() as conn:
        account = conn.execute(
            "SELECT account_id FROM accounts "
            "WHERE currency = ? AND type = ?",
            ("INR", "SYSTEM_TREASURY"),
        ).fetchone()[0]

        TransactionRepository(conn).create(
            transaction_id,
            "FUNDING",
            timestamp,
        )

        ledger = LedgerEntryRepository(conn)

        ledger.append(
            transaction_id=transaction_id,
            account_id=account,
            direction="DEBIT",
            amount_minor=500,
            currency="INR",
            created_at=timestamp,
        )

    return transaction_id


def test_hash_chain_verification(db, sample_transaction):
    with db.connection() as conn:
        ledger = LedgerEntryRepository(conn)
        report = ledger.verify_chain()

    assert report.overall_status == "PASS"
    assert report.entries_checked == 1


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE ledger_entries SET amount_minor = 900 WHERE entry_id = 1",
        "DELETE FROM ledger_entries WHERE entry_id = 1",
    ],
)
def test_ledger_immutability(db, sample_transaction, statement):
    with pytest.raises(
        sqlite3.IntegrityError, match="append-only"
    ), db.write_transaction() as conn:
        conn.execute(statement)


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE transactions SET description = ? WHERE transaction_id = ?",
        "DELETE FROM transactions WHERE transaction_id = ?",
    ],
)
def test_transaction_immutability(db, sample_transaction, statement):
    if statement.startswith("UPDATE"):
        parameters = ("Changed description", sample_transaction)
    else:
        parameters = (sample_transaction,)

    with pytest.raises(
        sqlite3.IntegrityError, match="append-only"
    ), db.write_transaction() as conn:
        conn.execute(statement, parameters)