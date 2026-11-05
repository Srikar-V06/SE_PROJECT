---
name: brain-ingest
description: Add new material (URL, document, or pasted text) to the Second Brain as a structured note with frontmatter, wikilinks, an index entry and a log entry. Use when asked to ingest, summarize, file, or save knowledge into brain/.
---

# brain-ingest

## Steps
1. Read AGENTS.md for the note schema, naming and wikilink rules.
2. Read brain/index.md to check whether a note on this topic already exists. If it does, update it instead of creating a duplicate.
3. If the source is long, save the raw text in brain/inbox/ first.
4. Write the note in brain/resources/ with the full frontmatter (title, type, status, created, updated, author, tags, sources, links, requirements).
5. Use the sections Summary, Key points, Relevance to this project. Write in your own words.
6. Add at least one [[wikilink]] to another note, and requirement IDs if they apply.
7. Add the note to brain/index.md under Resources with a short description.
8. Append one line to brain/log.md: date | ingest | note-name
9. List every source in the frontmatter. Do not invent facts. If a source cannot be read, say so.
10. Commit on a feature branch and open a PR for review.

## Based on
- [[agent-skills]]
- [[second-brain]]