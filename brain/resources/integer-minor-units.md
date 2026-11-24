---
title: Integer Minor Units
type: resource
status: active
created: 2026-11-12
updated: 2026-11-25
author: Vishwa-Pradyumna
tags: [money, precision, validation]
sources:
  - docs/SRS.pdf
  - docs/adr/ADR-002.md
links: ["[[double-entry-bookkeeping]]", "[[testing-strategy]]"]
requirements: [C-2, FR-2.6, BR-9, NFR-16, TQ-5]
---

## Summary

Financial amounts are represented as integer minor units
to avoid floating-point precision errors.

## Key points

- INR uses paise and USD uses cents.
- INR 100.50 is represented as 10050 minor units.
- Financial arithmetic uses integers.
- API monetary inputs must be strict integers.
- Floating-point values, strings and booleans are rejected.
- Posting amounts must be between 1 and 10^12 minor units.
- Zero is permitted for wallet balances but not for postings.
- Decimal input in the UI is converted using exact string logic.

## Relevance to this project

The Money domain type, wallet balances and ledger entries
use integer minor units.

Unit tests verify exact arithmetic and rejection of invalid
input types.