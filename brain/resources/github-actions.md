---
title: GitHub Actions
type: resource
status: active
created: 2026-11-12
updated: 2026-11-22
author: BharathVikas-T
tags: [ci, github-actions]
sources:
  - https://docs.github.com/en/actions/get-started/understand-github-actions
  - SDLC_and_Workflow.pdf
links: ["[[testing-strategy]]", "[[second-brain]]"]
requirements: [TQ-5, TQ-6, P-2]
---

## Summary
GitHub Actions runs repository workflows in response to events such as pushes and pull requests. A workflow is written in YAML, contains jobs, and runs its steps on a runner.

## Key points
- A workflow file lives under `.github/workflows/` and declares the events that start it.
- A workflow contains one or more jobs. Jobs run on runners, and their steps run shell commands or reusable actions.
- CI workflows can build and test proposed pull requests so the team can review a change alongside its check results.
- The project SDLC requires CI on pull requests for build, lint, tests, secret scanning, skill validation, and brain-note validation.
- In this repository's current `ci.yml` (checked 2026-11-22), build, lint, and test are placeholders; secret scanning and the two Python validators have commands configured.

## Relevance to this project
GitHub Actions is the project automation layer for the checks listed in [[testing-strategy]]. The current workflow still needs the Phase 3 implementation work assigned in the project plan; this note records the current placeholder state without treating the checks as complete.
