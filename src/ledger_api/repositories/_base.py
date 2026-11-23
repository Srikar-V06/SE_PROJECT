"""Shared SQLite repository helpers."""

import sqlite3

from ledger_api.domain.errors import ConflictError


def raise_conflict(exc: sqlite3.IntegrityError) -> None:
    """Translate SQLite uniqueness and referential-integrity failures."""
    raise ConflictError("record conflicts with existing database state") from exc
