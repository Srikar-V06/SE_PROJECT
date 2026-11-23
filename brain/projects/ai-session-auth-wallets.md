---
title: Phase 3 authentication and wallets
type: project
status: draft
created: 2026-11-23
updated: 2026-11-23
author: Srikar-V06
tags: [phase-3, authentication, wallets, ai-session]
sources: ["Final_Project_Plan_v2 (1).pdf", "docs/SRS.pdf", "docs/openapi.yaml", "docs/development-plan.md"]
links: ["[[authentication-sessions]]", "[[ai-session-phase3-backend-core]]", "[[testing-strategy]]"]
requirements: [FR-6, FR-1.1, FR-1.2, FR-1.3, FR-1.4, FR-1.7, NFR-9, NFR-10, NFR-13, A-2]
---

## Goal

Implement Srikar's Phase 3 assignment against the merged database foundation.
The four feature slices share one review branch at the owner's request.

## What worked

- Checked the foundation from [[ai-session-phase3-backend-core]] at main commit
  5ba7572. Initializing a fresh file twice produced seven business tables,
  one schema migration, INR and USD treasuries, and four immutability triggers.
  A new connection reported WAL, foreign keys enabled, a 5000 ms busy timeout
  and FULL synchronous mode. Issue #12 covers the earlier schema design.
- Followed [[authentication-sessions]] for Argon2id and digest-only storage.
  The login response carries the bearer token once as required by FR-6.2.
  Protected requests load the current database role.
- Exercised both local admin commands, duplicate registration, expiry, revocation,
  wallet ownership, and the static mount with isolated databases following
  [[testing-strategy]]. The package build included the CLI, migration and HTML.

## Gaps found before this assignment

- On the inspected main commit, the Stage 2 review, walkthrough, knowledge
  matrix and ADR-010 were absent. The traceability matrix lacked Issue, PR
  and test evidence. The changelog contained only Unreleased and the remote
  had no v0.1.0 tag. The GitHub issue listing contained only Issue #12.
- The merged foundation had a health test but no provider fakes or hash-chain
  tests. Its Money type allows zero balances and has no maximum. The planned
  1 to 10^12 limit for posting amounts still needs distinct input validation.
  These items belong to the broader phase. The connection, migrations and
  repositories required for auth and wallets were available.
- The initial Windows sandbox test run blocked during asyncio socket-pair
  creation. Running the same tests with local socket access succeeded.
