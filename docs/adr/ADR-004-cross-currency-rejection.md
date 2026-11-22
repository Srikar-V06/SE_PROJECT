# ADR-004: Cross-currency transfers are rejected

- Status: Accepted
- Date: 2026-11-20
- Requirements: FR-2.6, BR-2, DR-8, TBD-4
- Brain note: [[double-entry-bookkeeping]]
- Issue: #<issue-number>

## Context
The system holds INR and USD wallets. Moving money between currencies needs exchange rates, rounding rules and fees, which are out of scope for v1.0.

## Decision
- A transfer requires sender and receiver wallets of the same currency; otherwise it returns 422 CURRENCY_MISMATCH and writes nothing.
- Each currency has exactly one SYSTEM_TREASURY account (unique partial index), so per currency the wallet balances plus the treasury balance sum to zero.
- Every ledger entry's currency must equal its account's currency (database trigger).

## Consequences
- Double-entry checks and reconciliation work per currency with no conversion logic.
- Users who want a wallet in another currency must create a separate wallet and receive funding in it.
- Adding currencies later means seeding another treasury account.

## Alternatives considered
- FX conversion at transfer time: rejected, out of scope and adds rate and rounding risk.
- One shared treasury for all currencies: rejected, it breaks the zero-sum check per currency.