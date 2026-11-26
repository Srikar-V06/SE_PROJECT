# Changelog
## [Unreleased]
- Repository structure, Second Brain, brain-ingest skill
- Added README, CHANGELOG, and Issue and PR templates
- Added CI skeleton: placeholder build/lint/test, secret scan, SKILL.md and brain-note validators
- Added validator commands to AGENTS.md
- Added traceability matrix v0
- Added the Phase 3 SQLite database and migration foundation, including WAL, foreign-key enforcement, busy timeout, FULL synchronous mode, and atomic write transactions (00d443b).
- Added exact minor-unit money, clock/UUID/token providers, and parameterized repositories for users, sessions, accounts, wallets, transactions, and idempotency records (b9f33bd).
- Added append-only ledger entry creation and hash-chain verification, plus database/runtime ignore rules (20b3f26).
- Merged Phase 4 idempotency handling in PR #40: per-user keys, canonical request hashes, response replay, key-reuse conflicts, expiry and same-transaction persistence.
- Merged wallet funding in PR #41 using the shared posting and idempotency services.
- Merged owner-authorized wallet transfers in PR #42 with same-currency validation, guarded balance posting and idempotent response replay.
- Local Phase 4 verification follow-up: added funding/transfer API integration coverage and mapped service validation errors to HTTP 400; follow-up branch is pending review.
