---
title: MCP and Skills Reference
type: resource
status: active
created: 2026-11-12
updated: 2026-11-22
author: BharathVikas-T
tags: [mcp, skills, agents]
sources:
  - https://modelcontextprotocol.io/docs/getting-started/intro
  - https://agentskills.io/specification
  - SDLC_and_Workflow.pdf
links: ["[[agent-skills]]", "[[second-brain]]"]
requirements: [SK-1, SB-3]
---

## Summary
Model Context Protocol (MCP) and Agent Skills solve different problems. MCP is an open protocol for connecting AI applications to external systems, while an Agent Skill is a directory of task instructions that an agent can load when relevant.

## Key points
- MCP standardizes how AI applications connect to external data, tools, and workflows. A client and a server use the protocol to make those capabilities available to an application.
- An Agent Skill requires a directory containing `SKILL.md`. Its YAML frontmatter requires a `name` and `description`; the body holds the instructions. Scripts, references, and assets are optional.
- The skill name must match its parent directory. In this repository, each skill must also cite at least one distilled brain note under the project rules.
- MCP is not required to make a `SKILL.md` work; a skill can simply provide instructions to an agent. MCP can separately expose tools or data that a connected agent can use.

## Relevance to this project
This distinction helps the team maintain the local `skills/` workflows and understand how connected tools differ from repository instructions. The naming and note-citation rules come from [[agent-skills]] and [[second-brain]].
