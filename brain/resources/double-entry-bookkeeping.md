---
title: Double-Entry Bookkeeping
type: resource
status: active
created: 2026-11-12
updated: 2026-11-25
author: Vishwa-Pradyumna
tags: [accounting, ledger, transactions]
sources:
  - docs/SRS.pdf
  - docs/adr/ADR-003-append-only-ledger-reversals.md
  - docs/adr/ADR-004-cross-currency-rejection.md
links: ["[[integer-minor-units]]", "[[sqlite-acid-wal]]"]
requirements: [FR-4, FR-5, BR-1, BR-2, BR-3, BR-4]
---

## Summary

Double-entry bookkeeping records each financial transaction
using balanced debit and credit entries.

## Key points

- Every financial transaction must contain balanced entries.
- Total debits must equal total credits.
- Wallet balances equal their ledger credits minus debits.
- All entries in a transaction must use the appropriate currency.
- Financial postings must commit atomically.
- Existing ledger entries must never be modified or deleted.
- Corrections are recorded as compensating reversals.

## Relevance to this project

Wallet funding, transfers and reversals use double-entry
bookkeeping to preserve financial consistency.

Reconciliation verifies that transactions are balanced and
that cached wallet balances agree with the ledger.