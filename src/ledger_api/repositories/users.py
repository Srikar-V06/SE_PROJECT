"""Persistence operations for users."""

import sqlite3

from ledger_api.domain.errors import NotFoundError
from ledger_api.repositories._base import raise_conflict


class UserRepository:
    def grant_admin(self, normalized_email: str) -> None:
        result = self._connection.execute(
            "UPDATE users SET role = 'ADMIN' WHERE normalized_email = ?", (normalized_email,)
        )
        if not result.rowcount:
            raise NotFoundError("user not found")

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self,
        user_id: str,
        normalized_email: str,
        name: str,
        password_hash: str,
        role: str,
        created_at: str,
    ) -> None:
        try:
            self._connection.execute(
                "INSERT INTO users(user_id, normalized_email, name, password_hash, "
                "role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, normalized_email, name, password_hash, role, created_at),
            )
        except sqlite3.IntegrityError as exc:
            raise_conflict(exc)

    def get(self, user_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT user_id, normalized_email, name, password_hash, role, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("user not found")
        return row

    def get_by_email(self, normalized_email: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT user_id, normalized_email, name, password_hash, role, created_at "
            "FROM users WHERE normalized_email = ?",
            (normalized_email,),
        ).fetchone()
