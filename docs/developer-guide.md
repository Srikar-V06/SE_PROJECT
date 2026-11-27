# Developer Guide

## Prerequisites

- Python 3.11 or later.
- Git.
- Modern web browser.

## Repository structure

| Directory | Purpose |
|---|---|
| src/ledger_api | Application, domain, database and repositories |
| src/app | Administrator CLI |
| tests | Automated tests |
| docs | SRS, architecture, API and design documentation |
| brain | Project knowledge base |
| skills | Project skill definitions |
| scripts | Verification and validation scripts |

## Installation

Create and activate a Python virtual environment.

Install the dependencies from requirements.txt.

## Running the application

Run:

python -m uvicorn ledger_api.main:app --host 127.0.0.1 --port 8000

The application initializes SQLite through packaged migrations.

The default database path is data/ledger.sqlite3.
LEDGER_DB_PATH can be used to configure a different database.

## Running tests

python -m pytest -q

Database-dependent tests use isolated temporary SQLite files.

## Running coverage

python -m pytest --cov=ledger_api --cov=app --cov-report=term-missing

## Linting

Run Python lint checks:

```bash
python -m ruff check .
```

For frontend development, install the locked Node.js
development dependencies:

```bash
npm ci
```

Run JavaScript lint checks:

```bash
npm run lint:ui
```

The browser application is served by FastAPI at `/app/`.
Node.js is required only for frontend development checks,
not for serving the application.

## Building

python -m build

## Local verification

python scripts/local_check.py

The script builds, lints, tests, starts the application
and checks GET /health.

## Database rules

- WAL mode is enabled.
- Foreign keys are enforced.
- Financial writes use atomic transactions.
- Ledger history is append-only.
- Monetary values use integer minor units.

## Contribution workflow

- Create or select a GitHub Issue.
- Branch from main.
- Implement and test the task.
- Open a pull request.
- Obtain human review and passing CI.
- Merge through the reviewed pull request.

## References

- SRS.pdf
- architecture.md
- openapi.yaml
- development-plan.md
- test-plan.md

## Local HTTPS run mode

The ordinary HTTP development server is restricted to loopback.

For local HTTPS testing, generate a development-only certificate
using OpenSSL. Never commit certificates, private keys or
production credentials.

On macOS or Linux:

```bash
mkdir -p certs
umask 077

openssl req -x509 -newkey rsa:2048 -sha256 -nodes \
  -keyout certs/localhost.key \
  -out certs/localhost.crt \
  -days 30 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

Start the HTTPS server:

```bash
python -m uvicorn ledger_api.main:app \
  --host 127.0.0.1 \
  --port 8443 \
  --ssl-keyfile certs/localhost.key \
  --ssl-certfile certs/localhost.crt
```

Verify the health endpoint:

```bash
curl --cacert certs/localhost.crt https://localhost:8443/health
```

Expected response:

```json
{"status":"ok"}
```

The generated certificate is for local development only.
Non-loopback deployments require properly trusted HTTPS
certificates.