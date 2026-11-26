# Financial Ledger & Digital Wallet API

**Team Code Vibers:** Bharath (BT2024073), Pradyumna (BT2024157), Srikar (BT2024081), Haneesh (BT2024126)

## Short Description about the project
A backend for a digital wallet with a tamper-evident, double-entry ledger.
It supports idempotent transfers, safe concurrent balance updates, reversals and an administrative reconciliation check. Money is stored as integer minor units, and the database is SQLite.

## Status

Phase 3 - Core Implementation I.

Database foundation, authentication, wallet operations
and unit testing have been introduced.

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
repository participating in the operation.

## Run the API and provision administrators

From the repository root, install the project with `python -m pip install -e .`.
Run `python -m uvicorn ledger_api.main:app --host 127.0.0.1` and open
`http://127.0.0.1:8000/app/` or the interactive API at `/docs`.
Startup applies migrations to `data/ledger.sqlite3`. To use a different
database, set `LEDGER_DB_PATH` to the same absolute path for both the API and CLI.

Run the following commands locally with access to that database:

```powershell
python -m app.cli create-admin --email admin@example.org --name "Administrator"
python -m app.cli grant-admin --email existing-user@example.org
```

Creation prompts for a password without echoing it. Grant promotes an
existing account. Public registration creates a USER. Login returns a bearer
token valid for 30 minutes. Send it in the Authorization header as
`Bearer <token>`. Logout revokes that session.

## Documentation

- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [API Specification](docs/openapi.yaml)
- [Test Plan](docs/test-plan.md)