"""Atomic, per-user idempotency handling for financial operations."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from ledger_api.domain.errors import (
    IdempotencyKeyReused,
    ValidationError,
)
from ledger_api.providers.protocols import ClockProvider, DatabaseProvider
from ledger_api.repositories.idempotency import IdempotencyRepository

MINIMUM_RETENTION = timedelta(hours=24)


@dataclass(frozen=True, slots=True)
class OperationResponse:
    """Successful response data to persist and replay for a retry."""

    status_code: int
    body: Mapping[str, Any]
    transaction_id: str | None = None


@dataclass(frozen=True, slots=True)
class IdempotentResponse:
    """Operation response plus whether it came from the replay cache."""

    status_code: int
    body: dict[str, Any]
    transaction_id: str | None
    replayed: bool


def canonical_request_hash(
    user_id: str,
    operation: str,
    path_params: Mapping[str, Any],
    request_body: Mapping[str, Any],
) -> str:
    """Hash the user, operation, path parameters and canonical JSON body."""
    if not user_id or not operation.strip():
        raise ValidationError("user and operation are required for idempotency")
    canonical = {
        "user_id": user_id,
        "operation": operation,
        "path_params": dict(path_params),
        "body": dict(request_body),
    }
    try:
        encoded = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValidationError("request cannot be canonically serialized") from exc
    return hashlib.sha256(encoded).hexdigest()


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValidationError("idempotency clock must return a timezone-aware time")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise RuntimeError("stored idempotency expiry is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RuntimeError("stored idempotency expiry must include a timezone")
    return parsed.astimezone(UTC)


class IdempotencyService:
    """Run one financial action and persist its response atomically.

    The action receives the transaction's connection. It should call the
    posting engine using that connection and return only after all writes are
    ready to commit. Raising any exception rolls back the operation and key.
    """

    def __init__(
        self,
        db: DatabaseProvider,
        clock: ClockProvider,
        *,
        retention: timedelta = MINIMUM_RETENTION,
    ) -> None:
        if retention < MINIMUM_RETENTION:
            raise ValueError("idempotency retention must be at least 24 hours")
        self._db = db
        self._clock = clock
        self._retention = retention

    def execute(
        self,
        *,
        user_id: str,
        key: str,
        operation: str,
        path_params: Mapping[str, Any],
        request_body: Mapping[str, Any],
        action: Callable[[sqlite3.Connection], OperationResponse],
    ) -> IdempotentResponse:
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ValidationError("Idempotency-Key length must be 1 to 128 characters")
        request_hash = canonical_request_hash(
            user_id, operation, path_params, request_body
        )

        with self._db.write_transaction() as conn:
            repo = IdempotencyRepository(conn)
            current_time = self._clock.now()
            now_text = _timestamp(current_time)
            now = current_time.astimezone(UTC)
            existing = repo.get(user_id, key)

            if (
                existing is not None
                and _parse_timestamp(existing["expires_at"]) > now
            ):
                if existing["request_hash"] != request_hash:
                    raise IdempotencyKeyReused(
                        "Idempotency-Key was already used for a different request"
                    )
                return self._replay(existing)

            if existing is not None:
                repo.delete(user_id, key)

            response = action(conn)
            if not isinstance(response, OperationResponse):
                raise TypeError("idempotency action must return OperationResponse")
            if not 200 <= response.status_code < 300:
                raise ValidationError("idempotency action must return a success response")
            response_json = self._serialize_body(response.body)
            # Start retention after the operation and add a small commit margin.
            expires_at = _timestamp(
                self._clock.now() + self._retention + timedelta(minutes=1)
            )
            repo.save(
                user_id=user_id,
                key=key,
                operation=operation,
                request_hash=request_hash,
                response_status=response.status_code,
                response_body=response_json,
                transaction_id=response.transaction_id,
                created_at=now_text,
                expires_at=expires_at,
            )
            return IdempotentResponse(
                response.status_code,
                dict(response.body),
                response.transaction_id,
                replayed=False,
            )

    @staticmethod
    def _serialize_body(body: Mapping[str, Any]) -> str:
        try:
            return json.dumps(
                dict(body),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError("response cannot be stored as JSON") from exc

    @staticmethod
    def _replay(row: sqlite3.Row) -> IdempotentResponse:
        try:
            body = json.loads(row["response_body"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("stored idempotency response is invalid") from exc
        if not isinstance(body, dict):
            raise TypeError("stored idempotency response must be a JSON object")
        return IdempotentResponse(
            status_code=row["response_status"],
            body=body,
            transaction_id=row["transaction_id"],
            replayed=True,
        )
