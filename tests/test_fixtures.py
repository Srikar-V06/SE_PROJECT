def test_database_fixture(db):
    with db.connection() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    expected = {
        "users",
        "auth_sessions",
        "accounts",
        "wallets",
        "transactions",
        "ledger_entries",
        "idempotency_keys",
        "schema_migrations",
    }

    assert expected.issubset(tables)


def test_database_starts_empty(db):
    with db.connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

    assert count == 0


def test_fake_clock(fake_clock):
    before = fake_clock.now()

    fake_clock.advance(1800)

    difference = fake_clock.now() - before

    assert difference.total_seconds() == 1800


def test_fake_ids_are_unique(fake_ids):
    first = fake_ids.new_id()
    second = fake_ids.new_id()

    assert first != second


def test_fake_tokens_are_unique(fake_tokens):
    assert fake_tokens.generate_token() != fake_tokens.generate_token()