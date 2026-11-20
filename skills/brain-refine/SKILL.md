---
name: brain-refine
description: Organise the Second Brain by moving inbox notes into PARA folders, merging duplicates, fixing broken wikilinks and logging every change. Use after new notes are added or before a stage review.
---

# brain-refine

## When to use
After new notes are added, or before a stage review.

## Steps
1. Read AGENTS.md and brain/index.md.
2. For each note in brain/inbox/: decide its type (project, area, resource, archive)
   using the rules in AGENTS.md, set `type` in the frontmatter, move it to the
   matching folder, and add it to index.md.
3. Look for duplicate notes on the same topic. Propose a merge to the human.
   Keep every source URL. Never delete a note without human approval.
4. Run `python scripts/validate_brain.py`. Fix each broken [[wikilink]] by
   correcting the name or removing the link.
5. Check every note has requirement IDs and at least one link to another note.
6. Add one line per action to brain/log.md.
7. Run both validators and report what changed.

## Rules
- Do not invent facts or sources.
- Changes go through a pull request; record the AI session.

## Based on
[[second-brain]], [[ai-policy]]