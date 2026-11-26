---
title: Idempotency Keys
type: resource
status: active
created: 2026-11-12
updated: 2026-11-26
author: haneeshreddy9
tags: [idempotency, transactions, rest-api]
sources:
  - docs/SRS.pdf
  - docs/adr/ADR-006-idempotency.md
  - docs/openapi.yaml
links: ["[[race-conditions]]", "[[rest-api-design]]"]
requirements: [FR-2, FR-3.4, BR-8, NFR-18]
---

## Summary

Idempotency keys prevent duplicate financial transactions
when a client retries an uncertain request.

## Key points

- Funding, transfers and reversals require an Idempotency-Key.
- Keys are scoped to the authenticated user.
- Matching keys and request hashes replay the original response.
- Reusing a key with a different request returns a conflict.
- Key lookup occurs inside the same financial write transaction.
- Committed key records are retained for at least 24 hours.
- Rejected financial requests must not create committed key records.

## Relevance to this project

Idempotency prevents repeated network requests or UI submissions
from creating duplicate financial postings.

The implementation must coordinate idempotency records with
atomic ledger and balance changes.