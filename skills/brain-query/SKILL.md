---
name: brain-query
description: Answer project questions and draft SRS or ADR text using only the notes in brain/, citing each note used. Use before writing documents or when someone asks what the team decided.
---

# brain-query

## When to use
When someone asks "what did we decide about X?", or before drafting an SRS section
or an ADR.

## Steps
1. Read AGENTS.md and brain/index.md.
2. Pick the notes that match the question (by title, tags and requirement IDs) and
   read them.
3. Answer in a few sentences and cite each note as [[note-name]].
4. If the notes do not contain the answer, say so and suggest a new research note.
   Do not guess.
5. For an ADR draft, use the ADR template (Context, Decision, Alternatives,
   Consequences, Brain notes cited).
6. If a draft is saved, add a line to brain/log.md.

## Rules
- Use only facts found in the notes. Never invent sources.
- A human reviews every draft before it is merged.

## Based on
[[second-brain]], [[agent-skills]]