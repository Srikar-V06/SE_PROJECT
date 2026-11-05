---
title: Agent Skills
type: resource
status: done
created: 2026-11-05
updated: 2026-11-05
tags: [agents, skills]
sources: [Anthropic Agent Skills documentation]
links: [[second-brain]], [[ai-policy]]
---

## Summary
An Agent Skill is a folder of instructions that teaches an AI agent how to do a specific task. The agent reads a short description first and loads the full instructions only when the task needs them.

## Key points
- A skill is a folder containing a SKILL.md file.
- SKILL.md starts with YAML frontmatter: name and description.
- The description tells the agent when to use the skill.
- The body of SKILL.md holds the step-by-step instructions.
- A skill can also include extra files or scripts.
- Skills are loaded in stages, so they don't fill the agent's context.

## Relevance to this project
Our skills live in skills/<skill-name>/SKILL.md. The first one is brain-ingest, which adds new knowledge to the brain in a consistent format.