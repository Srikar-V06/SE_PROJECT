"""Persistence operations for immutable transaction headers."""

import sqlite3

from ledger_api.domain.errors import NotFoundError
from ledger_api.repositories._base import raise_conflict


class TransactionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self,
        transaction_id: str,
        transaction_type: str,
        created_at: str,
        *,
        description: str | None = None,
        reversal_of_transaction_id: str | None = None,
    ) -> None:
        try:
            self._connection.execute(
                "INSERT INTO transactions(transaction_id, type, "
                "reversal_of_transaction_id, description, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    transaction_id,
                    transaction_type,
                    reversal_of_transaction_id,
                    description,
                    created_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise_conflict(exc)

    def get(self, transaction_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT transaction_id, type, reversal_of_transaction_id, description, "
            "created_at FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("transaction not found")
        return row
    
    def get_reversal(
        self, transaction_id: str
    ) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT transaction_id, type, reversal_of_transaction_id, "
            "description, created_at FROM transactions "
            "WHERE reversal_of_transaction_id = ?",
            (transaction_id,),
        ).fetchone()
    def is_participant(
        self,
        transaction_id: str,
        user_id: str,
    ) -> bool:
        row = self._connection.execute(
            "SELECT 1 FROM ledger_entries AS entry "
            "JOIN wallets AS wallet "
            "ON wallet.account_id = entry.account_id "
            "WHERE entry.transaction_id = ? "
            "AND wallet.user_id = ? "
            "LIMIT 1",
            (transaction_id, user_id),
        ).fetchone()

        return row is not None

