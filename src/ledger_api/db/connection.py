"""Configured SQLite connections and atomic write transactions."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ledger_api.domain.errors import DatabaseBusyError


class SQLiteDatabase:
    """Provides short-lived SQLite connections configured for this service."""

    def __init__(self, path: str | Path, *, busy_timeout_ms: int = 5_000) -> None:
        self.path = Path(path)
        self.busy_timeout_ms = busy_timeout_ms
        if busy_timeout_ms <= 0:
            raise ValueError("busy_timeout_ms must be positive")

    def _open(self) -> sqlite3.Connection:
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            str(self.path),
            timeout=self.busy_timeout_ms / 1_000,
            isolation_level=None,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(f"PRAGMA busy_timeout = {int(self.busy_timeout_ms)}")
        conn.execute("PRAGMA synchronous = FULL")
        return conn

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield one configured connection and always close it afterwards."""
        conn = self._open()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def write_transaction(self) -> Iterator[sqlite3.Connection]:
        """Serialize a financial write and commit or roll it back as a unit."""
        with self.connection() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except sqlite3.OperationalError as exc:
                if conn.in_transaction:
                    conn.rollback()
                if self._is_busy(exc):
                    raise DatabaseBusyError("database is busy") from exc
                raise
            except Exception:
                if conn.in_transaction:
                    conn.rollback()
                raise

    def initialize(self) -> None:
        """Enable WAL and apply each packaged migration exactly once."""
        with self.connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            applied = {
                row[0]
                for row in conn.execute("SELECT version FROM schema_migrations")
            }
            migrations_dir = Path(__file__).parent / "migrations"
            for migration in sorted(migrations_dir.glob("[0-9]*.sql")):
                version = int(migration.name.split("_", 1)[0])
                if version in applied:
                    continue
                try:
                    conn.executescript(migration.read_text(encoding="utf-8"))
                except sqlite3.OperationalError as exc:
                    if self._is_busy(exc):
                        raise DatabaseBusyError("database is busy") from exc
                    raise

    @staticmethod
    def _is_busy(exc: sqlite3.OperationalError) -> bool:
        code = getattr(exc, "sqlite_errorcode", None)
        if code is not None and (code & 0xFF) in {
            sqlite3.SQLITE_BUSY,
            sqlite3.SQLITE_LOCKED,
        }:
            return True
        message = str(exc).lower()
        return "database is locked" in message or "database is busy" in message
