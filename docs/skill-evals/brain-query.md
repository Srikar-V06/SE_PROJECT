# Phase 2 Skill Evaluation: brain-query

Date: 2026-11-22

Skill: `skills/brain-query/SKILL.md`
Related: SK-3, SB-1, SB-3

## Method

Applied the skill's source-restricted answer process to two questions using the indexed brain notes. The evaluation is manual; it checks whether the answer is supported by notes and cites them, not whether an automated runner invoked the skill.

## Cases

### BQ-1: Answer a documented project decision

**Prompt:** “How does the project store and expire bearer sessions?”

**Expected:** Use the authentication note only, mention the project contract, and cite the note.

**Observed answer:** The project issues an opaque random bearer token at login with a 30-minute lifetime. It stores only the token's SHA-256 digest, checks expiry and revocation on each protected request, and revokes the server-side session at logout. [[authentication-sessions]]

**Result:** PASS. Each project-specific claim is in the cited note.

### BQ-2: Distinguish a project decision from a reference recommendation

**Prompt:** “What exact Argon2id settings did the project choose?”

**Expected:** Do not present OWASP's recommendation as a project decision; state the source-note limit and cite it.

**Observed answer:** The project requires Argon2id but the SRS does not choose implementation parameters. The note records OWASP's current minimum profile of 19 MiB, two iterations, and parallelism one as a reference recommendation, not as a project decision. [[authentication-sessions]]

**Result:** PASS. The answer keeps the distinction explicit and does not invent a configuration.

## Limitations

These cases cover a known answer and a source-boundary question; they do not establish that the skill answers every project topic correctly. A human reviewer should verify the cited note and the claims before merge. See [[agent-skills]] and [[ai-policy]].
