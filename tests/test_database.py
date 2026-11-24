import sqlite3

import pytest


def test_connection_settings(db):
    with db.connection() as conn:
        assert conn.execute(
            "PRAGMA journal_mode"
        ).fetchone()[0] == "wal"

        assert conn.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0] == 1

        assert conn.execute(
            "PRAGMA busy_timeout"
        ).fetchone()[0] == 5000

        assert conn.execute(
            "PRAGMA synchronous"
        ).fetchone()[0] == 2


def test_treasury_accounts(db):
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT currency, COUNT(*) "
            "FROM accounts "
            "WHERE type = ? "
            "GROUP BY currency",
            ("SYSTEM_TREASURY",),
        ).fetchall()

    assert {row[0]: row[1] for row in rows} == {
        "INR": 1,
        "USD": 1,
    }


def test_migration_is_not_repeated(db):
    db.initialize()

    with db.connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM schema_migrations"
        ).fetchone()[0]

    assert count == 1


def test_foreign_keys_enforced(db):
    with pytest.raises(
        sqlite3.IntegrityError, match="FOREIGN KEY"
    ), db.write_transaction() as conn:
        conn.execute(
            "INSERT INTO auth_sessions "
            "(session_id, user_id, token_digest, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                "fixture-session",
                "nonexistent-user",
                "test-digest",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:30:00Z",
            ),
        )