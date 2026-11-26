---
title: Race Conditions
type: resource
status: active
created: 2026-11-12
updated: 2026-11-26
author: haneeshreddy9
tags: [concurrency, sqlite, transactions]
sources:
  - docs/SRS.pdf
  - docs/adr/ADR-005-concurrency.md
  - docs/adr/ADR-009-hash-chain-entry-id.md
links: ["[[sqlite-acid-wal]]", "[[idempotency-keys]]"]
requirements: [FR-3, C-4, NFR-3, NFR-5]
---

## Summary

Race conditions occur when concurrent operations interact
with shared state without appropriate synchronization.

## Key points

- Financial balance checks and updates must occur atomically.
- SQLite permits only one writer at a time.
- BEGIN IMMEDIATE serializes financial write transactions.
- Idempotency lookup must occur inside the write transaction.
- Ledger entries, wallet balances and key records commit together.
- Failed writes must roll back without partial financial changes.
- Hash-chain entry identifiers are assigned under the write lock.

## Relevance to this project

The ledger uses serialized write transactions to prevent lost
updates, negative balances and duplicate financial postings.

Concurrency tests will verify these rules in later phases.