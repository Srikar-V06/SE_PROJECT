# AGENTS.md

Project: Financial Ledger & Digital Wallet API.
Read this file and brain/index.md before doing any work in this repo.

## Brain note schema
Every note in brain/ starts with this frontmatter:

---
title: Note title
type: project | area | resource | archive | inbox
status: draft | active | done
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: github-username
tags: []
sources: []
links: []
requirements: []
---

Field rules:
- author: the team member who wrote the note.
- sources: URLs or document names the note is based on.
- links: quoted wikilinks in a list, e.g. links: ["[[second-brain]]"]
- requirements: IDs such as FR-1, NFR-2, SK-1, SB-3 (empty list if none).

Resource notes use these sections: Summary, Key points, Relevance to this project.

## PARA folders
- brain/inbox/: unsorted new material
- brain/projects/: active work with deadlines (stage reviews, ai-session notes)
- brain/areas/: ongoing responsibilities
- brain/resources/: reference and research notes
- brain/archive/: inactive items
- brain/index.md: entry point, lists every note
- brain/log.md: one line per brain action

## Wikilink conventions
- Link notes with [[note-name]] (no path, no .md).
- Link a note on its first mention.
- Every note links to at least one other note.
- Link notes to requirement IDs, Issues and PRs (example: Related: FR-2, Issue #12, PR #15).
- Every new note is added to brain/index.md.

## Note naming
- Lowercase, hyphens, short names. Example: second-brain.md
- Name the file after the concept, no dates in the name.
- AI session notes: ai-session-topic.md
- ADRs live in docs/adr/ as ADR-001.md, ADR-002.md, and so on.

## Skills directory
- Skills live in skills/<skill-name>/SKILL.md
- The folder name must match the name in the SKILL.md frontmatter.
- Current skills: brain-ingest, brain-refine, brain-query, local-check
- Planned skills: simulate-transfer
- Every skill cites at least one brain note.

## Rules for AI-assisted development
- AI assistants are allowed, but the team is responsible for every line merged.
- A human reviews every AI-generated change in a PR. No direct pushes of AI work to main.
- Every member must be able to explain anything merged.
- Brain changes, including AI changes, go through PRs.
- AI reads brain/index.md and the relevant notes before coding or writing docs.
- Every AI-assisted change to the brain is logged in brain/log.md.
- Record significant AI sessions as ai-session notes (goal, what worked, what failed).
- Never paste secrets, tokens or credentials into any AI tool or note.
- Do not use real financial data in prompts or notes.
- Every ADR cites at least one brain note.
- Tests must pass before merge. AI must not edit tests just to make them pass.
- Do not invent facts or sources. If a source cannot be read, say so.
- Before opening a PR, run `python scripts/validate_brain.py` and `python scripts/validate_skills.py`.

## Project commands

Run from the repository root with Python 3.11 or later
and an activated virtual environment.

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Build

```bash
python -m build
```

### Lint

```bash
python -m ruff check .
```

### Test

```bash
python -m pytest -q
```

### Coverage

```bash
python -m pytest --cov=ledger_api --cov=app --cov-report=term-missing
```

### Start local HTTP server

```bash
python -m uvicorn ledger_api.main:app --host 127.0.0.1 --port 8000
```

### Create administrator

```bash
python -m app.cli create-admin --email admin@example.org --name Administrator
```

### Grant administrator

```bash
python -m app.cli grant-admin --email existing-user@example.org
```

### Local verification

```bash
python scripts/local_check.py
```

### Validate project documentation

```bash
python scripts/validate_brain.py
python scripts/validate_skills.py
python scripts/audit_brain.py
```

For HTTPS setup, refer to docs/developer-guide.md.
Generated certificates and private keys must never be committed.
