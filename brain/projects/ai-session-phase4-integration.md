---
title: Phase 4 integration and negative tests
type: project
status: draft
created: 2026-11-27
updated: 2026-11-27
author: Srikar-V06
tags: [integration, regression, phase-4]
sources: ["docs/test-plan.md", "docs/defect-log.md", "tests/test_financial_integration.py"]
links: ["[[testing-strategy]]", "[[ai-session-phase4-api-verification]]", "[[idempotency-keys]]"]
requirements: [TQ-2, TQ-4, TQ-6, NFR-21, FR-2.8, FR-3.4, NFR-18]
---

## Goal

Complete Srikar's Phase 4 integration and negative checks on main at
`fea160f`, following [[testing-strategy]], and start the defect log.

## What worked

The HTTP tests apply the fake clock to [[idempotency-keys]], renew the expired
login, and retry on either side of the stored key expiry. Other cases verify
independent callers, rollback of balances and ledger writes after a key-save
failure, and rejection of malformed IDs and headers. All 80 tests passed.

## What failed

The injected storage failure interrupted a transfer after posting. A separate
connection saw the original balances and row counts, and a retry succeeded.
The new tests revealed no additional product defect. The defect log records
the earlier self-transfer error from [[ai-session-phase4-api-verification]]
and its regression test in PR #43.
