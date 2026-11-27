---
title: Hash Chain Integrity
type: resource
status: active
created: 2026-11-27
updated: 2026-11-27
author: haneeshreddy9
tags: [ledger, hash-chain, integrity, sha256]
sources:
  - docs/SRS.pdf
  - docs/design/hash-chain.md
  - docs/adr/ADR-009-hash-chain-entry-id.md
links: ["[[double-entry-bookkeeping]]", "[[sqlite-acid-wal]]"]
requirements: [FR-4.5, FR-5.4]
---

## Summary

A hash chain links each ledger entry to the preceding
entry using a SHA-256 digest.

## Key points

- The first entry uses the genesis previous hash.
- Entry hashes include the stored transaction fields
  and the sequential entry ID.
- Entry IDs and hashes are calculated before insertion.
- Ledger entries are appended inside the same write
  transaction as the financial operation.
- Verification recomputes entry hashes in ascending order.
- Verification reports the first failing entry.

## Relevance to this project

The hash chain supports ledger integrity verification
and the administrative reconciliation feature.

The hash chain supplements database immutability
constraints but does not replace access controls.