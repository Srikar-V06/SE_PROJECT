# AGENTS.md

## Brain note schema
Every note in brain/ starts with this frontmatter:

---
title: Note title
type: project | area | resource | archive | inbox
status: draft | active | done
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
sources: []
links: []
---

## Wikilink conventions
- Link notes with [[note-name]] (no path, no .md).
- Link a note on its first mention.
- Every note links to at least one other note.
- Every new note is added to brain/index.md.

## Note naming
- Lowercase, hyphens, short names. Example: second-brain.md
- Name the file after the concept, no dates in the name.

## Skills directory
- Skills live in skills/<skill-name>/SKILL.md
- Current skills: brain-ingest

## Rules for AI-assisted development
- AI suggests, humans review. No AI code is merged without review.
- AI reads brain/index.md and relevant notes before coding.
- Every AI-assisted change is logged in brain/log.md.
- No secrets or real financial data in prompts or notes.
- Decisions and reasons are saved in brain/, not only in chat.
- Tests must pass before commit. AI must not edit tests just to make them pass.