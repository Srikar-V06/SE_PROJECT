# ADR-009: SHA-256 hash chain with entry_id assigned under the write lock

- Status: Accepted
- Date: 2026-11-20
- Requirements: FR-4.5, FR-5.4, TBD-3
- Brain note: [[hash-chain-integrity]]
- Issue: #<issue-number>

## Context
Triggers stop casual edits, but someone with direct database access could still disable them and alter rows. The ledger needs tamper-evidence that reconciliation can verify.

## Decision
- `entry_hash = SHA-256(prev_hash | transaction_id | account_id | direction | amount | currency | timestamp | entry_id)`, fields joined with `|`, UTF-8, lowercase hex output.
- The genesis `prev_hash` is 64 zero characters.
- Because `entry_id` is part of the hash, it is chosen before the insert: inside `BEGIN IMMEDIATE` the writer reads the last entry, uses `entry_id = last + 1`, computes the hash, then inserts with that explicit id.
- Reconciliation recomputes the chain in `entry_id` order and reports the first broken entry.
- Full details: `docs/design/hash-chain.md`.

## Consequences
- Any change to a past entry breaks every later link and is detected.
- Hashing happens inside the single write lock, so financial writes stay serialized (already required by C-4).
- The chain proves integrity but not authenticity; an attacker who rewrites the whole chain consistently is not detected unless hashes are anchored externally.

## Alternatives considered
- Database-generated autoincrement id: rejected, the id is unknown until after the insert.
- Excluding `entry_id` from the hash: rejected, it lets entries be reordered undetected.
- External hash anchoring: deferred to a later version (TBD-3).