# ADR-003: Append-only ledger with reversals

- Status: Accepted
- Date: 2026-11-20
- Requirements: FR-4.2, FR-4.3, FR-4.4, BR-4, TBD-6
- Brain note: [[double-entry-bookkeeping]]
- Issue: #<issue-number>

## Context
Money history must be verifiable. If rows can be edited or deleted, balances and audits cannot be trusted. Mistakes still need a way to be corrected.

## Decision
- No UPDATE or DELETE of `transactions` or `ledger_entries`: the API exposes none, and database triggers reject both independently.
- A correction is a new REVERSAL transaction with opposite entries, linked to the original through a UNIQUE `reversal_of_transaction_id`.
- An original transaction can be reversed once (second attempt: 409 ALREADY_REVERSED).
- A REVERSAL cannot be reversed (409 REVERSAL_OF_REVERSAL).
- A reversal that would make a wallet negative is rejected (422 REVERSAL_OVERDRAW).
- Reversal is ADMIN-only and requires an Idempotency-Key.

## Consequences
- Full history is always visible to both participants.
- The UNIQUE link enforces "reverse once" at the database level.
- Corrections cost extra rows; there is no partial or deferred reversal in v1.0.
- `auth_sessions` and the wallet balance cache are mutable and are not ledger records (DR-12).

## Alternatives considered
- Editing or deleting wrong rows: rejected, it destroys auditability.
- Soft-delete flags: rejected, it is still an update and breaks the hash chain.
- Partial reversals: deferred to a later version.