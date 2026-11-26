---
title: AI Session - Phase 3 Project Commands and Local Verification
type: project
status: draft
created: 2026-11-26
updated: 2026-11-26
author: haneeshreddy9
tags: [ai, phase-3, documentation, local-check, https, testing]
sources:
  - Final se plan.pdf
  - docs/SRS.pdf
  - AGENTS.md
  - README.md
  - docs/developer-guide.md
  - scripts/local_check.py
  - skills/local-check/SKILL.md
links: ["[[ai-policy]]", "[[testing-strategy]]", "[[github-actions]]", "[[skill-eval-local-check]]", "[[authentication-sessions]]"]
requirements: [SK-4, NFR-15, TQ-6, P-2, P-4]
---

## Goal

Complete the Phase 3 project command documentation,
local HTTPS setup and local-check skill improvements.

Ensure that team members can install, build, test and
run the application consistently.

## AI assistance

AI assistance was used to:

- Review the existing project commands and documentation.
- Identify missing development and verification commands.
- Prepare local HTTPS setup instructions.
- Improve database isolation in the local-check script.
- Update the local-check skill instructions.
- Diagnose dependency and Ruff linting errors.

## Changes made

- Updated AGENTS.md with installation, build, lint, test,
  server startup and admin CLI commands.
- Updated README.md to reflect Phase 3 implementation.
- Added local HTTPS instructions to the developer guide.
- Excluded locally generated certificates through .gitignore.
- Updated scripts/local_check.py to use a fresh temporary
  SQLite database for server verification.
- Updated skills/local-check/SKILL.md to document database
  isolation and full automated test execution.

## What worked

- Project dependencies were installed in a Python
  virtual environment.
- The financial-ledger-api package installed successfully.
- Ruff identified an import-ordering issue in the updated
  local-check script.
- The linting issue was diagnosed without requiring changes
  to the application logic.

## What failed

The initial Ruff check reported an I001 import-ordering
error in scripts/local_check.py after adding the os import.

The suggested correction was to arrange imports according
to the repository's Ruff configuration.


## Safety considerations

- Local verification uses an isolated temporary database.
- The development server listens on the loopback interface.
- Locally generated certificates and private keys must
  not be committed.
- No real financial data, passwords or session tokens
  are included in the documentation.

## Human review

The changes must be reviewed by a teammate before merging
into main.

## Related branch

docs/agents-commands

## Conclusion

The Phase 3 project commands, HTTPS documentation and
local-check improvements have been prepared for verification
and pull request review.