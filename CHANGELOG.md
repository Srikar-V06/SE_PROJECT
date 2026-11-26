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
- Phase 4 local work: added reusable per-user idempotency handling with canonical request hashes, response replay, key-reuse conflicts, expiry and same-transaction persistence; this branch is not yet linked to a GitHub Issue or PR.
