# ADR-005: Concurrency Control with SQLite

Status: Proposed | Date: 2026-11-22 | Author: Vishwa-Pradyumna

## Context

Concurrent financial requests must not cause lost updates, negative
balances or duplicate ledger transactions.

## Decision

- Enable SQLite WAL mode.
- Use BEGIN IMMEDIATE for financial write transactions.
- Configure a five-second busy timeout.
- Enable foreign keys and FULL synchronous mode.
- Commit ledger entries, balances and idempotency records atomically.
- Return 503 DB_BUSY when the write lock cannot be acquired in time.

## Alternatives considered

- Application-level locking.
- Deferred SQLite transactions.
- A separate database server.

## Consequences

Financial writes are serialized, preventing conflicting balance
updates. Concurrent reads remain possible under WAL mode.

## Related Requirements

FR-3, C-1, C-4, NFR-5, NFR-7.

## Brain notes cited

[[race-conditions]], [[sqlite-acid-wal]]