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
- Phase 4 local work pending review: added ADMIN-only wallet funding using the shared posting and idempotency services. Concurrency relies on the existing SQLite `BEGIN IMMEDIATE` write transaction and idempotent replay protection.
