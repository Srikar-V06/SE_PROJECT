---
title: Agent Skills
type: resource
status: done
created: 2026-11-05
updated: 2026-11-05
author: Srikar-V06
tags: [agents, skills]
sources: [https://agentskills.io, SDLC_and_Workflow.pdf]
links: ["[[second-brain]]", "[[ai-policy]]"]
requirements: [SK-1, SB-3]
---

## Summary
An Agent Skill is a folder of instructions that teaches an AI agent how to do a specific task. The agent reads a short description first and loads the full instructions only when the task needs them.

## Key points
- A skill is a folder containing a SKILL.md file.
- SKILL.md starts with YAML frontmatter, with name and description as the required fields.
- The name should match the folder name and use lowercase letters and hyphens.
- The description says what the skill does and when to use it.
- The body of SKILL.md holds the step-by-step instructions.
- A skill can include extra files such as scripts and reference documents.
- Skills load in stages (description first, full body when needed), so they don't fill the agent's context.

## Relevance to this project
Our skills live in skills/<skill-name>/SKILL.md. The first one is brain-ingest, which adds new knowledge to the brain in a consistent format. Later skills are brain-refine, brain-query, local-check and simulate-transfer. Each skill must cite at least one brain note, see [[second-brain]] and [[ai-policy]].