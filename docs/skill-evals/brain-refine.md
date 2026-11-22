# Phase 2 Skill Evaluation: brain-refine

Date: 2026-11-22

Skill: `skills/brain-refine/SKILL.md`
Related: SK-2, SB-1, SB-2, SB-5

## Method

Applied the skill to the current repository after completing the Bharath-owned notes. Each case checks the expected behavior from the skill instructions; the evaluation is a manual task run, not a separate automated harness.

## Cases

### BR-1: Refine an incomplete new resource note

**Prompt:** “Refine the brain after adding the authentication-sessions resource note.”

**Expected:** Read `AGENTS.md` and the index; verify the note schema, source, required resource sections, links and requirements; add an index entry and log line; do not invent research.

**Observed:** The placeholder source and empty body were replaced with a summary based on `docs/SRS.pdf` and the two linked OWASP pages. The note has all resource sections, project requirements, two wikilinks, an index entry, and a brain-log entry.

**Result:** PASS.

### BR-2: Audit the shared vault without taking over teammate notes

**Prompt:** “Run a refinement pass over the current shared brain.”

**Expected:** Check inbox and index coverage, identify incomplete or duplicate notes, and respect each note's author.

**Observed:** The inbox had no unsorted material; all existing resource notes were indexed. Six collaborator-owned resource notes were found to be stubs with incomplete frontmatter and no research content. They were flagged with their authors in the index and pass report; they were not rewritten. No merge was justified from the available content.

**Result:** PASS with owner follow-up. The vault as a whole is not yet schema-complete.

### BR-3: Validate repository artifacts

**Prompt:** “Run the brain and skill validators after the refinement.”

**Expected:** Both validator scripts exit successfully; manual checks cover rules those scripts do not implement.

**Observed:** `python scripts/validate_brain.py` and `python scripts/validate_skills.py` both passed after edits. A separate manual audit was needed because the brain validator does not enforce required fields, resource sections, placeholder removal, or index completeness. That audit still found six collaborator-owned stubs; they are listed for their authors in the index and pass report.

**Result:** PASS for validator execution and for detecting/reporting the remaining owner follow-up. The shared vault is not yet fully schema-complete.

## Limitations

The evaluation found that the old `brain-refine` instructions did not require a complete schema/resource-section audit or explicitly protect teammate-authored notes. Those checks and ownership rules were added to the skill. The current validator remains less strict than the project schema, so the skill must still include a manual review step. See [[second-brain]] and [[ai-policy]].
