from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from ledger_api.auth import AuthService
from ledger_api.db import SQLiteDatabase
from ledger_api.main import app


class FakeClock:
    def __init__(self):
        self.current_time = datetime(2026, 1, 1, tzinfo=UTC)

    def now(self):
        return self.current_time

    def advance(self, seconds):
        self.current_time += timedelta(seconds=seconds)


class FakeIdProvider:
    def __init__(self):
        self.counter = 0

    def new_id(self):
        self.counter += 1
        return str(UUID(int=self.counter))


class FakeTokenProvider:
    def __init__(self):
        self.counter = 0

    def generate_token(self):
        self.counter += 1
        return f"test-only-token-{self.counter}"


@pytest.fixture
def db(tmp_path):
    database = SQLiteDatabase(tmp_path / "test.sqlite3")
    database.initialize()
    return database


@pytest.fixture
def fake_clock():
    return FakeClock()


@pytest.fixture
def fake_ids():
    return FakeIdProvider()


@pytest.fixture
def fake_tokens():
    return FakeTokenProvider()


@pytest.fixture
def auth_service(db, fake_clock, fake_ids, fake_tokens):
    return AuthService(db, fake_clock, fake_ids, fake_tokens)


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setenv("LEDGER_DB_PATH", str(db.path))

    with TestClient(app) as test_client:
        yield test_client