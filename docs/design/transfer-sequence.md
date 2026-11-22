# Transfer Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Transfer Service
    participant D as Repository / SQLite

    C->>A: Transfer request with bearer token and key
    A->>A: Authenticate and validate request
    A->>S: Process transfer
    S->>D: BEGIN IMMEDIATE
    S->>D: Look up idempotency key

    alt Matching existing request
        D-->>S: Stored response
        S->>D: Release transaction
        S-->>A: Replayed response
    else Different request with same key
        S->>D: ROLLBACK
        S-->>A: 409 Conflict
    else New request
        S->>D: Check ownership, balance and currency
        S->>D: Insert ledger entries
        S->>D: Update wallet balances
        S->>D: Store idempotency response
        S->>D: COMMIT
        S-->>A: Transfer created
    end

    A-->>C: HTTP response
```

Any failed business check or database operation rolls back all
pending financial writes. A database lock timeout returns 503 DB_BUSY.

Related requirements: FR-2, FR-3, FR-4, FR-6.

Reference: SRS Appendix B.4.