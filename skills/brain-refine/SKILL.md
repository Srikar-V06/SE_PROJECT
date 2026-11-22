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
4. Audit every note in brain/ except index.md and log.md for all required
   frontmatter fields, at least one valid [[wikilink]], requirement IDs (or an
   explicit empty list), and index coverage. Resource notes also need Summary,
   Key points, and Relevance to this project sections. Flag placeholder sources
   or placeholder body text; never invent sources or project facts to fill them.
5. Check the `author` before changing an existing note. For a note authored by
   another team member, record the missing information and ask its author to
   update it through the related issue or PR. Do not silently rewrite it.
6. Run `python scripts/validate_brain.py`. Fix each broken [[wikilink]] by
   correcting the name or removing the link, and manually check the note schema
   because the validator only checks frontmatter presence and link targets.
7. Add one line per brain action to brain/log.md.
8. Run both validators and report completed work separately from owner follow-up.

## Rules
- Do not invent facts or sources.
- Changes go through a pull request; record the AI session.

## Based on
[[second-brain]], [[ai-policy]]
