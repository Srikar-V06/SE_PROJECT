from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier, Lock
from time import sleep

import pytest

from ledger_api.domain.errors import (
    IdempotencyKeyReused,
    ValidationError,
)
from ledger_api.repositories.users import UserRepository
from ledger_api.services.idempotency import (
    IdempotencyService,
    OperationResponse,
    canonical_request_hash,
)

OPERATION = "wallet.fund"
PATH_PARAMS = {"wallet_id": "wallet-1"}
REQUEST_BODY = {"amount_minor": 750}


@pytest.fixture
def idempotency_user(db, fake_ids):
    user_id = fake_ids.new_id()
    with db.write_transaction() as conn:
        UserRepository(conn).create(
            user_id,
            "idempotency-user@example.org",
            "Idempotency Test User",
            "test-only-password-hash",
            "USER",
            "2026-01-01T00:00:00Z",
        )
    return user_id


@pytest.fixture
def idempotency_service(db, fake_clock):
    return IdempotencyService(db, fake_clock)


def run_action(service, user_id, action, *, key="request-key", body=None):
    return service.execute(
        user_id=user_id,
        key=key,
        operation=OPERATION,
        path_params=PATH_PARAMS,
        request_body=REQUEST_BODY if body is None else body,
        action=action,
    )


def test_request_hash_is_stable_and_scoped():
    expected = canonical_request_hash(
        "user-1", OPERATION, {"a": 1, "b": 2}, {"amount_minor": 750}
    )
    reordered = canonical_request_hash(
        "user-1", OPERATION, {"b": 2, "a": 1}, {"amount_minor": 750}
    )

    assert expected == reordered
    assert expected != canonical_request_hash(
        "user-2", OPERATION, {"a": 1, "b": 2}, {"amount_minor": 750}
    )
    assert expected != canonical_request_hash(
        "user-1", "wallet.transfer", {"a": 1, "b": 2}, {"amount_minor": 750}
    )


def test_success_is_replayed_for_same_key_and_request(
    idempotency_service, idempotency_user
):
    calls = 0

    def action(_connection):
        nonlocal calls
        calls += 1
        return OperationResponse(201, {"transaction_id": "transaction-1"})

    first = run_action(idempotency_service, idempotency_user, action)
    second = run_action(idempotency_service, idempotency_user, action)

    assert first.status_code == second.status_code == 201
    assert first.body == second.body == {"transaction_id": "transaction-1"}
    assert first.replayed is False
    assert second.replayed is True
    assert calls == 1


def test_same_key_with_different_request_is_conflict(
    idempotency_service, idempotency_user
):
    first = run_action(
        idempotency_service,
        idempotency_user,
        lambda _conn: OperationResponse(201, {"ok": True}),
    )
    calls = 0

    def should_not_run(_connection):
        nonlocal calls
        calls += 1
        return OperationResponse(201, {"ok": True})

    with pytest.raises(IdempotencyKeyReused) as caught:
        run_action(
            idempotency_service,
            idempotency_user,
            should_not_run,
            body={"amount_minor": 751},
        )

    assert caught.value.code == "IDEMPOTENCY_KEY_REUSED"
    assert first.replayed is False
    assert calls == 0


def test_expired_key_is_reused(idempotency_service, idempotency_user, fake_clock):
    calls = 0

    def action(_connection):
        nonlocal calls
        calls += 1
        return OperationResponse(201, {"attempt": calls})

    first = run_action(idempotency_service, idempotency_user, action)
    fake_clock.advance(timedelta(hours=24, minutes=1).total_seconds())
    second = run_action(idempotency_service, idempotency_user, action)

    assert first.body == {"attempt": 1}
    assert second.body == {"attempt": 2}
    assert second.replayed is False
    assert calls == 2


def test_action_failure_rolls_back_operation_and_key(
    idempotency_service, idempotency_user, db
):
    def failing_action(conn):
        conn.execute(
            "INSERT INTO transactions(transaction_id, type, created_at) "
            "VALUES (?, ?, ?)",
            ("failed-transaction", "FUNDING", "2026-01-01T00:00:00Z"),
        )
        raise RuntimeError("posting failed")

    with pytest.raises(RuntimeError, match="posting failed"):
        run_action(idempotency_service, idempotency_user, failing_action)

    with db.connection() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE transaction_id = ?",
            ("failed-transaction",),
        ).fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM idempotency_keys WHERE user_id = ?",
            (idempotency_user,),
        ).fetchone()[0] == 0


def test_concurrent_identical_requests_execute_once(
    idempotency_service, idempotency_user, db
):
    start = Barrier(2)
    calls = 0
    calls_lock = Lock()

    def action(_connection):
        nonlocal calls
        with calls_lock:
            calls += 1
            current_call = calls
        sleep(0.05)
        return OperationResponse(201, {"attempt": current_call})

    def request():
        start.wait(timeout=3)
        return run_action(idempotency_service, idempotency_user, action)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _index: request(), range(2)))

    assert calls == 1
    assert sorted(result.replayed for result in results) == [False, True]
    assert results[0].body == results[1].body == {"attempt": 1}
    with db.connection() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM idempotency_keys WHERE user_id = ?",
            (idempotency_user,),
        ).fetchone()[0] == 1


@pytest.mark.parametrize("key", ["", "x" * 129])
def test_invalid_key_is_rejected_before_action(
    idempotency_service, idempotency_user, key
):
    calls = 0

    def action(_connection):
        nonlocal calls
        calls += 1
        return OperationResponse(201, {"ok": True})

    with pytest.raises(ValidationError):
        run_action(idempotency_service, idempotency_user, action, key=key)

    assert calls == 0


def test_retention_cannot_be_shorter_than_24_hours(db, fake_clock):
    with pytest.raises(ValueError, match="at least 24 hours"):
        IdempotencyService(db, fake_clock, retention=timedelta(hours=23))
