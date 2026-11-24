import hashlib
import secrets

import pytest

from ledger_api.auth import (
    Credentials,
    Registration,
    Unauthenticated,
    digest,
    timestamp,
)
from ledger_api.repositories.sessions import SessionRepository


def test_token_digest():
    expected = hashlib.sha256(b"example-test-token").hexdigest()

    assert digest("example-test-token") == expected


def test_password_hashing(auth_service):
    password = secrets.token_urlsafe(24)

    user = auth_service.register(
        Registration(
            email="fixture@example.org",
            name="Test User",
            password=password,
        )
    )

    with auth_service.db.connection() as conn:
        stored_hash = conn.execute(
            "SELECT password_hash FROM users WHERE user_id = ?",
            (user.user_id,),
        ).fetchone()[0]

    assert stored_hash.startswith("$argon2id$")
    assert stored_hash != password
    assert auth_service.hasher.verify(stored_hash, password)


def test_session_expiry(auth_service, fake_clock):
    password = secrets.token_urlsafe(24)

    user = auth_service.register(
        Registration(
            email="session@example.org",
            name="Session Test",
            password=password,
        )
    )

    login = auth_service.login(
        Credentials(
            email="session@example.org",
            password=password,
        )
    )

    token = login["token"]

    assert login["expires_in"] == 1800
    assert auth_service.authenticate(token).user.user_id == user.user_id

    fake_clock.advance(1799)

    assert auth_service.authenticate(token).user.user_id == user.user_id

    fake_clock.advance(1)

    with pytest.raises(Unauthenticated):
        auth_service.authenticate(token)


def test_revoked_session(auth_service, fake_clock):
    password = secrets.token_urlsafe(24)

    auth_service.register(
        Registration(
            email="logout@example.org",
            name="Logout Test",
            password=password,
        )
    )

    login = auth_service.login(
        Credentials(
            email="logout@example.org",
            password=password,
        )
    )

    token = login["token"]
    principal = auth_service.authenticate(token)

    with auth_service.db.write_transaction() as conn:
        SessionRepository(conn).revoke(
            principal.session_id,
            timestamp(fake_clock.now()),
        )

    with pytest.raises(Unauthenticated):
        auth_service.authenticate(token)