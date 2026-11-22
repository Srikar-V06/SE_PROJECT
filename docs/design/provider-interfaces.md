# Provider Interfaces

## Purpose

Providers isolate external dependencies from business logic so that
services can be tested independently.

## Proposed Interfaces

```python
from typing import Protocol, ContextManager
from datetime import datetime
import sqlite3


class DatabaseProvider(Protocol):
    def connection(self) -> ContextManager[sqlite3.Connection]:
        ...

    def write_transaction(self) -> ContextManager[sqlite3.Connection]:
        ...


class ClockProvider(Protocol):
    def now(self) -> datetime:
        ...


class IdProvider(Protocol):
    def new_id(self) -> str:
        ...


class TokenProvider(Protocol):
    def generate_token(self) -> str:
        ...
```

## Responsibilities

### DatabaseProvider

Provides configured SQLite connections and manages write transactions.
A write transaction commits on success and rolls back on failure.
All repositories participating in one financial operation share the
same connection.

### ClockProvider

Returns the current UTC time for ledger timestamps, session expiry
and idempotency expiry.

### IdProvider

Generates UUIDs for users, accounts, wallets, sessions and transactions.
Ledger entry IDs remain sequential integers.

### TokenProvider

Generates secure opaque session tokens with at least 256 bits of
randomness.

## Test Fakes

| Provider | Test implementation |
|---|---|
| DatabaseProvider | Fresh isolated temporary SQLite database |
| ClockProvider | Fixed UTC time that tests can advance |
| IdProvider | Predictable sequence of valid UUIDs |
| TokenProvider | Predictable test-only tokens |

Test implementations must never be used in production.

## Related Requirements

C-3, DR-10, NFR-10, NFR-23, TQ-1.

## References

- [System Architecture](../architecture.md)
- [[testing-strategy]]
- [[authentication-sessions]]