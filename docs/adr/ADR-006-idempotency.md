# ADR-006: Per-User Idempotency Keys

Status: Proposed | Date: 2026-11-22 | Author: Vishwa-Pradyumna

## Context

A client may retry a financial request after a network failure.
Repeated requests must not create duplicate transactions.

## Decision

- Require an Idempotency-Key for funding, transfers and reversals.
- Scope each key to the authenticated user.
- Store a SHA-256 hash of the user ID, operation, path parameters
  and canonical request body.
- Replay the original response for matching requests.
- Return 409 IDEMPOTENCY_KEY_REUSED for mismatched requests.
- Retain committed key records for at least 24 hours.
- Store idempotency records inside the financial write transaction.

## Alternatives considered

- Globally unique idempotency keys.
- Client-side duplicate prevention only.

## Consequences

Retries do not produce additional financial postings within the
retention period. Additional database storage is required.

## Related Requirements

FR-2, FR-3.4, BR-8, NFR-18.

## Brain notes cited

[[idempotency-keys]]