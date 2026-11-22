---
title: SQLite ACID and WAL
type: resource
status: active
created: 2026-11-12
updated: 2026-11-22
author: Vishwa-Pradyumna
tags: [sqlite, transactions, concurrency, wal]
sources:
  - https://www.sqlite.org/wal.html
  - https://www.sqlite.org/lang_transaction.html
  - https://www.sqlite.org/pragma.html
  - docs/SRS.pdf
links: ["[[race-conditions]]", "[[idempotency-keys]]"]
requirements: [FR-3, C-1, C-4, NFR-5, NFR-7]
---

## Summary

SQLite provides transactional guarantees required for reliable
financial operations. Write-Ahead Logging improves concurrency
between readers and writers.

## Key points

- Atomic transactions prevent partially committed transfers.
- WAL allows concurrent reading while a writer is active.
- SQLite permits only one writer at a time.
- BEGIN IMMEDIATE acquires the write transaction before
  balance checks and financial updates.
- A busy timeout allows requests to wait for a database lock.
- FULL synchronous mode improves commit durability.

## Relevance to this project

The wallet system uses BEGIN IMMEDIATE and WAL to serialize
financial writes. Ledger entries, wallet balances and idempotency
records must commit together or roll back together.

These decisions are documented in ADR-005.