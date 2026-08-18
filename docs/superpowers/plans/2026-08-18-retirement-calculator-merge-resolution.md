# Retirement Calculator Merge Resolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve PR #124 against the latest `main`, verify the integrated site, and merge the pull request.

**Architecture:** Merge the latest `main` into the isolated feature worktree once, reconcile the shared site builder at source level, and regenerate versioned HTML and sitemap outputs from the resolved builder. Treat `artifacts/**` as derived output so the generator remains the source of truth.

**Tech Stack:** Python 3, static HTML/CSS/JavaScript, Git, GitHub pull requests

**Spec:** `docs/superpowers/plans/2026-08-18-retirement-abroad-calculator-seo.md`

## Global Constraints

- Preserve the retirement calculator, passive-income assumptions, SEO comparison table, structured data, internal links, and downloadable PNG assets.
- Preserve unrelated changes already landed on `main`.
- Do not hand-edit generated HTML when the unified build script can regenerate it.
- Run the complete build, static verification, unit-test, and whitespace checks before pushing or merging.

---

### Task 1: Integrate latest main and regenerate derived outputs

**Files:**
- Modify: `src/build_unified_app.py`
- Regenerate: `artifacts/**/*.html`
- Regenerate: `artifacts/sitemap.xml`
- Preserve: retirement calculator source, data, tests, and PNG assets already committed on the feature branch

**Interfaces:**
- Consumes: latest `main` at `FETCH_HEAD` and the existing retirement calculator implementation
- Produces: one conflict-free feature branch containing both change sets

- [ ] **Step 1: Start a non-fast-forward merge without committing**

Run: `git merge --no-commit FETCH_HEAD`

Expected: Git reports conflicts in the shared builder and generated artifacts.

- [ ] **Step 2: Reconcile the source builder**

Compare the merge-base, `main`, and feature versions of `src/build_unified_app.py`. Retain the latest `main` behavior and the feature additions that register the retirement calculator page, internal links, canonical metadata, schema, and sitemap entry. Remove all conflict markers.

- [ ] **Step 3: Reset conflicted generated outputs to main and rebuild**

Use the `main` side for conflicted files under `artifacts/`, then run `python3 src/build_unified_app.py` so the resolved builder recreates all derived pages and `artifacts/sitemap.xml`.

- [ ] **Step 4: Confirm no merge markers or unresolved paths remain**

Run: `git diff --check`

Run: `git diff --name-only --diff-filter=U`

Expected: both commands exit successfully and the unresolved-path command prints nothing.

### Task 2: Verify, publish, and merge PR #124

**Files:**
- Test: `tests/`
- Verify: generated `artifacts/`

**Interfaces:**
- Consumes: the resolved branch from Task 1
- Produces: a tested merge-resolution commit and merged GitHub PR #124

- [ ] **Step 1: Run the complete build and static verification**

Run: `python3 src/build_unified_app.py`

Run: `python3 scripts/verify_static_site.py --min-sitemap-urls 66`

Expected: both commands exit 0.

- [ ] **Step 2: Run the complete unit-test suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 3: Run final repository checks**

Run: `git diff --check`

Run: `git status --short`

Expected: no whitespace errors and only intended merge-resolution changes are present.

- [ ] **Step 4: Commit and push the resolution**

Commit message: `merge: resolve retirement calculator conflicts with main`

Push the feature branch through the repository's authorized SSH remote.

- [ ] **Step 5: Recheck PR #124 and merge**

Confirm the PR head matches the pushed commit and is mergeable, then merge with the squash method through the connected GitHub integration.
