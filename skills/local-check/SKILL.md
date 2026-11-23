---
name: local-check
description: Build, lint, test and start the local application, then verify the health endpoint and report PASS or FAIL.
---

# Local Check

## Purpose

Verify the local application before opening a pull request.

## Prerequisites

- Python 3.11 or later.
- Project dependencies installed from requirements.txt.
- Commands executed from the repository root.

## Steps

Run the local verification script:

```bash
python scripts/local_check.py
```

The script performs five checks:

1. Build the Python package.
2. Run Ruff lint checks.
3. Run automated tests using pytest.
4. Start the local FastAPI server.
5. Call GET /health and verify its response.

Print PASS or FAIL for each check. Return a non-zero exit
code if any check fails.

Stop the server started by the script after the check.

## Rules

- Never use production credentials or databases.
- Never expose passwords or bearer tokens.
- Do not change tests to hide failures.
- Report failures honestly.

## Related Requirements

SK-4, TQ-6, P-2.

## Based on

[[testing-strategy]], [[github-actions]]