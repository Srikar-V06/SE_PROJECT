"""Persistence operations for user-scoped idempotency records."""

import sqlite3

from ledger_api.domain.errors import ConflictError, ValidationError


class IdempotencyRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self, user_id: str, key: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT user_id, key, operation, request_hash, response_status, "
            "response_body, transaction_id, created_at, expires_at "
            "FROM idempotency_keys WHERE user_id = ? AND key = ?",
            (user_id, key),
        ).fetchone()

    def save(
        self,
        *,
        user_id: str,
        key: str,
        operation: str,
        request_hash: str,
        response_status: int,
        response_body: str,
        created_at: str,
        expires_at: str,
        transaction_id: str | None = None,
    ) -> None:
        if not 1 <= len(key) <= 128:
            raise ValidationError("idempotency key length must be between 1 and 128")
        try:
            self._connection.execute(
                "INSERT INTO idempotency_keys(user_id, key, operation, request_hash, "
                "response_status, response_body, transaction_id, created_at, expires_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    key,
                    operation,
                    request_hash,
                    response_status,
                    response_body,
                    transaction_id,
                    created_at,
                    expires_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("idempotency key already exists or user is unknown") from exc
