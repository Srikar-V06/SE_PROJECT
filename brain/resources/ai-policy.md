---
title: AI-Assisted Development Policy
type: resource
status: done
created: 2026-11-05
updated: 2026-11-05
author: Srikar-V06
tags: [policy, ai, sdlc]
sources: [SDLC_and_Workflow.pdf]
links: ["[[second-brain]]", "[[agent-skills]]"]
requirements: [SB-2, SB-3, SB-5, SB-6]
---

## Summary
The project SDLC expects the team to use AI coding assistants, but the team stays fully responsible for everything that is merged. Every AI-generated change must be reviewed by a human in a pull request. Significant AI sessions are recorded in the brain, and secrets are never shared with AI tools.

## Key points
- AI coding assistants are expected and allowed for code, skills and documents.
- The team is responsible for every line merged.
- A human reviews every AI-generated change in a PR, with at least one review on every PR (code, skills and brain).
- Every member must be able to explain any merged code, skill or document in project reviews.
- Significant AI sessions are recorded as ai-session notes (goal, what worked, what failed).
- Never paste secrets, tokens or credentials into any AI tool.
- Brain changes, including AI changes, go through PRs.
- Every ADR and every skill cites at least one distilled brain note.
- A short review note is written at the end of each stage (what worked, what did not, what to change).
- The four SDLC stages are Requirements, Design, Testing and CI, and Review.

## Relevance to this project
These rules are the basis of the "Rules for AI-assisted development" section in AGENTS.md. They apply to every stage of the Ledger project and to the brain itself. They apply to the use of [[agent-skills]] and to how [[second-brain]] changes are reviewed.