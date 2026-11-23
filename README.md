# Financial Ledger & Digital Wallet API

**Team Code Vibers:** Bharath (BT2024073), Pradyumna (BT2024157), Srikar (BT2024081), Haneesh (BT2024126)

## Short Description about the project
A backend for a digital wallet with a tamper-evident, double-entry ledger.
It supports idempotent transfers, safe concurrent balance updates, reversals and an administrative reconciliation check. Money is stored as integer minor units, and the database is SQLite.

## Status
Stage 1 – Requirements (in progress).

## Repository layout
- `brain/`: team knowledge base (Obsidian vault, PARA folders)
- `skills/`: agent skills (`SKILL.md` folders)
- `docs/`: SRS, design, test plan, ADRs
- `tests/`: automated tests (added in Phase 3)
- `scripts/`: validators and helper scripts
- `.github/`: CI workflow and Issue/PR templates
- `AGENTS.md`: rules for the brain and for AI assistants

## How to contribute
1. Create or pick an Issue.
2. Branch from `main` (`feat/...`, `docs/...`, `fix/...`).
3. Open a PR with the template filled in.
4. Get one review and a green CI.
5. Merge.

## Backend foundation

The Phase 3 backend package uses Python 3.11 or later and the Python
standard library. Install it from the repository root and initialize a
SQLite database with:

```powershell
python -m pip install -e .
python -c "from ledger_api.db import SQLiteDatabase; SQLiteDatabase('data/ledger.sqlite3').initialize()"
```

The database provider enables WAL, foreign keys, a five-second busy timeout
and FULL synchronous mode. Financial writes should use
`SQLiteDatabase.write_transaction()` and pass its connection to every
repository participating in the operation. API/server commands will be
added with the API layer.
