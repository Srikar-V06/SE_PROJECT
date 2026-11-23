# Development Plan

## Overview

This document describes the implementation tasks for Phases 3 to 6
of the Financial Ledger and Digital Wallet API.

Source: SRS v2.0 and Final Project Plan.

Each task must have a GitHub Issue, an assigned owner, a dedicated
branch, reviewed pull request and passing CI checks.

## Phase 3 - Core Implementation I

| Task | Owner | Branch |
|---|---|---|
| Project structure | Bharath | feat/project-structure |
| SQLite database connection | Bharath | feat/db-connection |
| Database migrations | Bharath | feat/migrations-schema |
| Immutability triggers | Bharath | feat/immutability-triggers |
| Money type and validation | Bharath | feat/money-type |
| Provider implementations | Bharath | feat/providers |
| Repositories | Bharath | feat/repositories |
| Error handling | Bharath | feat/error-handling |
| Hash chain function | Bharath | feat/hash-chain-function |
| Password hashing and sessions | Srikar | feat/auth-passwords-sessions |
| Authentication endpoints | Srikar | feat/auth-endpoints |
| Admin provisioning CLI | Srikar | feat/admin-cli |
| Wallet endpoints | Srikar | feat/wallet-endpoints |
| Isolated database fixtures | Pradyumna | test/unit-fixtures |
| Core unit tests | Pradyumna | test/unit-core |
| Authentication unit tests | Pradyumna | test/unit-auth |
| User and developer guides | Haneesh | docs/user-dev-docs |
| Project commands | Haneesh | docs/agents-commands |
| AI session records | Haneesh | docs/ai-sessions-phase3 |

Existing database, domain and ledger foundation work is recorded in
PRs #21, #22, #23 and #25. Verify the remaining acceptance criteria
before marking the corresponding tasks as complete.

## Phase 4 - Core Implementation II

| Task | Owner | Branch |
|---|---|---|
| Atomic transaction posting | Haneesh | feat/post-transaction |
| Ledger hash chain integration | Haneesh | feat/hash-chain-engine |
| Reversals | Haneesh | feat/reversals |
| Ledger and transaction reads | Haneesh | feat/ledger-reads |
| Idempotency handling | Bharath | feat/idempotency |
| Wallet funding | Bharath | feat/funding |
| Transfers | Bharath | feat/transfers |
| Concurrency protection | Bharath | feat/concurrency |
| Integration tests | Srikar | test/integration |
| Negative tests | Srikar | test/negative |
| Defect tracking | Srikar | docs/defect-log |
| API documentation and user guide | Pradyumna | docs/api-docs-user-guide |
| Web UI shell | Pradyumna | feat/ui-shell |

Release milestone: v0.2.0.

## Phase 5 - Advanced Features and Testing

| Task | Owner | Branch |
|---|---|---|
| Reconciliation | Pradyumna | feat/reconciliation |
| Transfer UI | Pradyumna | feat/ui-transfer |
| History and admin UI | Pradyumna | feat/ui-history-admin |
| UI accessibility | Pradyumna | feat/ui-accessibility |
| Security hardening | Haneesh | feat/security-hardening |
| Simulate-transfer skill | Haneesh | feat/simulate-transfer |
| System tests | Bharath | test/system |
| Concurrency tests | Bharath | test/concurrency |
| Security tests | Bharath | test/security |
| CI hardening | Bharath | ci/hardening |
| SRS updates | Srikar | docs/srs-update |
| Reconciliation ADR | Srikar | docs/adr-007 |
| Browser tests | Srikar | test/ui-browser |

Release milestone: v0.3.0.

## Phase 6 - Review and Release

| Task | Owner | Branch |
|---|---|---|
| Final cleanup | Srikar | fix/final-cleanup |
| Final integrity tests | Srikar | test/final-integrity |
| Demo script and rehearsal | Pradyumna | test/final-demo |
| Traceability and release preparation | Haneesh | docs/final-release |
| Final documentation | Bharath | docs/final-documentation |
| Final brain refinement | Bharath | docs/brain-final-pass |

Release milestone: v1.0.0.

## Dependencies

- Database connections and migrations precede API implementation.
- Authentication precedes protected wallet operations.
- Ledger posting precedes funding, transfers and reversals.
- API implementation precedes full UI integration.
- Reconciliation requires the ledger and hash chain implementation.
- Every functional requirement must have automated verification.

## Definition of Done

- Requirement and Issue linked.
- Implementation or documentation completed.
- Relevant tests passed.
- CI checks passed.
- Human review completed.
- Traceability matrix and project records updated.