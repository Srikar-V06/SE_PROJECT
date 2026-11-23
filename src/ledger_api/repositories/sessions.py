"""Persistence operations for digest-only authentication sessions."""

import sqlite3

from ledger_api.domain.errors import ConflictError, NotFoundError


class SessionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        session_id: str,
        user_id: str,
        token_digest: str,
        created_at: str,
        expires_at: str,
    ) -> None:
        try:
            self._connection.execute(
                "INSERT INTO auth_sessions(session_id, user_id, token_digest, "
                "created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, user_id, token_digest, created_at, expires_at),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("session conflicts with existing database state") from exc

    def get_active_by_digest(self, token_digest: str, now: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT session_id, user_id, token_digest, created_at, expires_at, revoked_at "
            "FROM auth_sessions WHERE token_digest = ? AND revoked_at IS NULL "
            "AND expires_at > ?",
            (token_digest, now),
        ).fetchone()

    def revoke(self, session_id: str, revoked_at: str) -> None:
        cursor = self._connection.execute(
            "UPDATE auth_sessions SET revoked_at = ? "
            "WHERE session_id = ? AND revoked_at IS NULL",
            (revoked_at, session_id),
        )
        if cursor.rowcount != 1:
            exists = self._connection.execute(
                "SELECT 1 FROM auth_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if exists is None:
                raise NotFoundError("session not found")
