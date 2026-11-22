---
title: Testing Strategy
type: resource
status: active
created: 2026-11-12
updated: 2026-11-22
author: BharathVikas-T
tags: [testing, pytest, ci]
sources:
  - docs/SRS.pdf
  - https://docs.pytest.org/en/stable/explanation/fixtures.html
  - https://docs.github.com/en/actions/get-started/understand-github-actions
links: ["[[github-actions]]", "[[ai-policy]]"]
requirements: [TQ-1, TQ-2, TQ-3, TQ-4, TQ-5, TQ-6, P-2]
---

## Summary
The SRS maps testing to unit, integration, system, negative/security, and CI checks. Each test should start from controlled data so its result can be repeated and failures can be traced to a specific requirement.

## Key points
- Unit tests cover arithmetic, double-entry balance, exact minor units, request hashing, password hashing, and token validation (TQ-1).
- Integration tests cover commit and rollback behavior, owner-scoped queries, session expiry and revocation, and idempotency scope (TQ-2).
- System tests cover the required user and admin workflows end to end; negative and security tests cover invalid input, authorization, idempotency conflicts, concurrency, and token leakage (TQ-3, TQ-4).
- Pytest fixtures provide reusable, explicit test setup such as a known database or test data. Function-scoped fixtures can give tests separate fresh state and cleanup.
- CI must use isolated test data and run on pushes and pull requests. Significant defects need regression coverage; the SRS also requires skill evaluations before stage submissions (TQ-5, TQ-6).
- The SDLC requires checks for build, lint, tests, secret scanning, SKILL.md validation, and brain-note validation; see [[github-actions]].

## Relevance to this project
These requirements guide the planned test suite and its CI workflow. Until implementation begins, they describe the verification plan rather than results; the team should record actual outcomes when each test stage is run.
