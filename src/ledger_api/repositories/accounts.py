"""Persistence operations for ledger accounts."""

import sqlite3

from ledger_api.repositories._base import raise_conflict


class AccountRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self, account_id: str, account_type: str, currency: str, created_at: str
    ) -> None:
        try:
            self._connection.execute(
                "INSERT INTO accounts(account_id, type, currency, created_at) "
                "VALUES (?, ?, ?, ?)",
                (account_id, account_type, currency, created_at),
            )
        except sqlite3.IntegrityError as exc:
            raise_conflict(exc)

    def get(self, account_id: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT account_id, type, currency, created_at FROM accounts "
            "WHERE account_id = ?",
            (account_id,),
        ).fetchone()

    def get_treasury(self, currency: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT account_id, type, currency, created_at FROM accounts "
            "WHERE type = 'SYSTEM_TREASURY' AND currency = ?",
            (currency,),
        ).fetchone()
