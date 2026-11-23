"""Persistence operations for wallets, including guarded balance changes."""

import sqlite3

from ledger_api.domain.errors import (
    ConflictError,
    InsufficientFundsError,
    NotFoundError,
)
from ledger_api.repositories._base import raise_conflict


class WalletRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self,
        wallet_id: str,
        user_id: str,
        account_id: str,
        currency: str,
        created_at: str,
    ) -> None:
        try:
            self._connection.execute(
                "INSERT INTO wallets(wallet_id, user_id, account_id, currency, "
                "balance_minor, created_at) VALUES (?, ?, ?, ?, 0, ?)",
                (wallet_id, user_id, account_id, currency, created_at),
            )
        except sqlite3.IntegrityError as exc:
            raise_conflict(exc)

    def get(self, wallet_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT wallet_id, user_id, account_id, currency, balance_minor, created_at "
            "FROM wallets WHERE wallet_id = ?",
            (wallet_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("wallet not found")
        return row

    def get_for_user(self, user_id: str, currency: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT wallet_id, user_id, account_id, currency, balance_minor, created_at "
            "FROM wallets WHERE user_id = ? AND currency = ?",
            (user_id, currency),
        ).fetchone()

    def apply_delta(self, wallet_id: str, delta_minor: int) -> int:
        """Atomically adjust a balance, rejecting any result below zero."""
        if delta_minor == 0:
            return self.get(wallet_id)["balance_minor"]
        cursor = self._connection.execute(
            "UPDATE wallets SET balance_minor = balance_minor + ? "
            "WHERE wallet_id = ? AND balance_minor + ? >= 0",
            (delta_minor, wallet_id, delta_minor),
        )
        if cursor.rowcount != 1:
            exists = self._connection.execute(
                "SELECT 1 FROM wallets WHERE wallet_id = ?", (wallet_id,)
            ).fetchone()
            if exists is None:
                raise NotFoundError("wallet not found")
            if delta_minor < 0:
                raise InsufficientFundsError("wallet balance is insufficient")
            raise ConflictError("wallet balance could not be updated")
        return self.get(wallet_id)["balance_minor"]
