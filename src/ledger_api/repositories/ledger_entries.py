"""Append and verify immutable ledger entries."""

from __future__ import annotations

import sqlite3

from ledger_api.domain.errors import ValidationError
from ledger_api.ledger.hash_chain import GENESIS_HASH, compute_entry_hash
from ledger_api.ledger.verification import VerificationReport, verify_entries


class LedgerEntryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def append(
        self,
        *,
        transaction_id: str,
        account_id: str,
        direction: str,
        amount_minor: int,
        currency: str,
        created_at: str,
    ) -> int:
        """Append one entry; caller must hold the shared BEGIN IMMEDIATE lock."""
        if not self._connection.in_transaction:
            raise RuntimeError("ledger entries must be appended in a write transaction")
        if direction not in {"CREDIT", "DEBIT"}:
            raise ValidationError("direction must be CREDIT or DEBIT")
        if isinstance(amount_minor, bool) or not isinstance(amount_minor, int) or amount_minor <= 0:
            raise ValidationError("ledger amount must be a positive integer")
        if currency not in {"INR", "USD"}:
            raise ValidationError("unsupported ledger currency")
        if any("|" in value for value in (transaction_id, account_id, created_at)):
            raise ValidationError("ledger fields cannot contain the hash separator")

        previous = self._connection.execute(
            "SELECT entry_id, entry_hash FROM ledger_entries "
            "ORDER BY entry_id DESC LIMIT 1"
        ).fetchone()
        entry_id = 1 if previous is None else int(previous["entry_id"]) + 1
        prev_hash = GENESIS_HASH if previous is None else previous["entry_hash"]
        entry_hash = compute_entry_hash(
            prev_hash,
            transaction_id,
            account_id,
            direction,
            amount_minor,
            currency,
            created_at,
            entry_id,
        )
        self._connection.execute(
            "INSERT INTO ledger_entries(entry_id, transaction_id, account_id, "
            "direction, amount_minor, currency, prev_hash, entry_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                entry_id,
                transaction_id,
                account_id,
                direction,
                amount_minor,
                currency,
                prev_hash,
                entry_hash,
                created_at,
            ),
        )
        return entry_id

    def get_for_transaction(self, transaction_id: str) -> list[sqlite3.Row]:
        return list(
            self._connection.execute(
                "SELECT entry_id, transaction_id, account_id, direction, amount_minor, "
                "currency, prev_hash, entry_hash, created_at FROM ledger_entries "
                "WHERE transaction_id = ? ORDER BY entry_id",
                (transaction_id,),
            )
        )

    def verify_chain(self) -> VerificationReport:
        """Verify ledger entries in ascending entry ID order."""

        rows = self._connection.execute(
            "SELECT entry_id, transaction_id, account_id, direction, "
            "amount_minor, currency, prev_hash, entry_hash, created_at "
            "FROM ledger_entries ORDER BY entry_id ASC"
        )

        return verify_entries(rows)