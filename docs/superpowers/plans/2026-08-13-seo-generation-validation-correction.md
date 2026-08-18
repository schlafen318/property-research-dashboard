# SEO Generation Validation Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increase valid SEO proposal generation without weakening deterministic safety controls.

**Architecture:** Keep the existing structured-output schema and validator. Improve the model instruction at `build_generation_input()` and replace single-token entity detection with a small helper that detects only consecutive capitalized proper-name phrases.

**Tech Stack:** Python 3.11, `unittest`, OpenAI Responses structured outputs, GitHub Actions.

## Global Constraints

- Non-guide pages must return null FAQ fields.
- Proposed titles must contain 30–65 characters.
- Proposed meta descriptions must contain 70–165 characters.
- Protected-topic language remains rejected deterministically.
- Ordinary sentence-start words must not be classified as entities.

---

### Task 1: Page-aware generation instructions

**Files:**
- Modify: `scripts/seo_content_generator.py`
- Test: `tests/test_seo_content_generator.py`

**Interfaces:**
- Consumes: `build_generation_input(finding: dict, context: TargetPageContext) -> list[dict]`
- Produces: a developer message containing explicit page type, null-field, and character-bound instructions.

- [ ] **Step 1: Write the failing test**

Add a test that joins the developer-message content and asserts it contains `country`, `FAQ fields must be null`, `30 to 65 characters`, `70 to 165 characters`, and protected-topic fields must be null.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_seo_content_generator.OpenAIGenerationTests.test_generation_prompt_is_page_aware_and_length_bounded -v`

Expected: FAIL because the current developer message lacks these explicit constraints.

- [ ] **Step 3: Write minimal implementation**

Extend `build_generation_input()` with a page-specific instruction derived from `context.page_type`. For non-guide pages require both FAQ fields to be null. State the exact title and meta-description character bounds and require null for any field that would introduce protected-topic language.

- [ ] **Step 4: Run test to verify it passes**

Run the focused test and expect PASS.

- [ ] **Step 5: Commit**

Commit the prompt test and implementation as `Make SEO generation instructions page-aware`.

### Task 2: Entity false-positive correction

**Files:**
- Modify: `scripts/seo_content_generator.py`
- Test: `tests/test_seo_content_generator.py`

**Interfaces:**
- Produces: `_capitalized_entity_phrases(text: str) -> set[str]`, returning consecutive multiword capitalized phrases.
- Consumes: `validate_proposal(proposal: ContentProposal, context: TargetPageContext) -> list[str]`.

- [ ] **Step 1: Write the failing regression test**

Add a test showing `More research. Which market fits?` does not generate a capitalized-entity error, while `New York research.` does when `New York` is absent from the source context.

- [ ] **Step 2: Run test to verify it fails**

Run the focused regression test and expect FAIL because `More` and `Which` are currently treated as entities.

- [ ] **Step 3: Write minimal implementation**

Create `_capitalized_entity_phrases()` using a regex that returns sequences of two or more capitalized words. Compare complete phrases case-insensitively against source text, and report only unsupported phrases.

- [ ] **Step 4: Run focused and full verification**

Run the focused test, all unit tests, Python compilation, `src/build_unified_app.py`, static-site verification, tracking verification, and the fixture feedback-loop dry run.

- [ ] **Step 5: Commit and publish**

Commit as `Avoid SEO entity validation false positives`, push the branch, open and merge a PR into `main`, trigger `SEO feedback loop`, then inspect `generated_content` in the completed run logs.
