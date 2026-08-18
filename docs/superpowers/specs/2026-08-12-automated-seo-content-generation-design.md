# Automated SEO Content Generation Design

**Date:** 2026-08-12
**Status:** Approved for implementation planning

## Objective

Extend the existing SEO feedback loop so qualified Search Console findings produce real, reviewable content changes instead of proposal-only Markdown files. Generated changes must remain in a draft pull request until approved and must never introduce unsupported legal, tax, visa, ownership, price, or return claims.

## Current State

The daily workflow already:

- reads Search Console and sitemap data;
- classifies CTR, near-ranking, and content-gap opportunities;
- creates deduplicated issues;
- opens proposal-only draft pull requests for editorial changes;
- implements deterministic internal links;
- rebuilds and validates the static site;
- deploys merged changes and reports results in issue #1.

The missing stage is the conversion of an editorial finding into constrained source content that the existing site builder can render.

## Approaches Considered

### 1. Structured content overrides in a machine-owned data file — selected

The model returns a schema-constrained content proposal. Deterministic application code validates it and writes approved fields to `data/seo_content_overrides.json`. The existing site builder reads these overrides when rendering pages.

This approach isolates generated content from application code, produces small auditable diffs, and makes rollback straightforward.

### 2. Model-generated patches to `src/build_unified_app.py`

The model could return or author a Python diff directly. This would require less builder refactoring, but it would mix probabilistic output with executable code and make validation and recovery substantially harder. This approach is rejected.

### 3. Fully autonomous content publishing

The model could generate, merge, and deploy content without review. This minimizes manual effort but creates unacceptable editorial and factual risk for international property content. This approach is rejected for editorial changes. Existing deterministic internal-link auto-merges remain unchanged.

## Scope

### Included in the first release

- Existing-page `query-ctr-opportunity` findings.
- Existing-page `low-ctr-opportunity` findings.
- Existing-page `near-ranking-opportunity` findings that require more than a deterministic internal link.
- Title tag, meta description, one FAQ question and answer, limited intro refinement, and contextual internal-link anchor text.
- One consolidated draft pull request per daily run.

### Excluded from the first release

- Automatically publishing or merging editorial content.
- New landing-page generation.
- New factual claims or externally researched assertions.
- Changes to prices, yields, taxes, laws, visas, ownership rules, or investment returns.
- Rewriting destination data, scores, methodology, or listing evidence.
- Replacing the existing deterministic internal-link automation.

Content-gap findings continue to create human-review candidates until the existing-page generator has accumulated a reliable validation history.

## Architecture

### Content context collector

A new module reads each qualified finding and resolves its canonical target URL. It extracts only the context needed to revise that page:

- current title, meta description, H1, intro, and FAQs;
- Search Console query, impressions, CTR, and average position;
- permitted internal-link targets already present in the sitemap;
- the site's editorial constraints and research caveats;
- the finding fingerprint and a hash of the current source content.

The collector must reject ambiguous target resolution. A model is never asked to choose between unrelated pages.

### Structured content generator

A new `scripts/seo_content_generator.py` calls the OpenAI Responses API. It uses Structured Outputs with a strict schema, following the official OpenAI guidance for schema-constrained model output: <https://developers.openai.com/api/docs/guides/structured-outputs>.

The model is configurable through `SEO_CONTENT_MODEL`; the initial default is `gpt-5.6`. The API credential is supplied only through the GitHub Actions secret `OPENAI_API_KEY`.

Every output contains these required fields, with `null` used when a field should remain unchanged:

- finding fingerprint;
- target canonical URL;
- base content hash;
- revised title;
- revised meta description;
- revised intro;
- FAQ question;
- FAQ answer;
- internal-link target;
- internal-link anchor text;
- rationale tied to the Search Console signal;
- list of source text fragments used to support the rewrite;
- policy flags indicating whether prohibited claim categories were encountered.

The model does not receive write access, repository tools, or web-browsing tools. It returns content data only.

### Policy and quality validator

A deterministic validator runs before any file is changed. It rejects a proposal when:

- its URL, fingerprint, or base hash does not match the input;
- it names an internal-link target outside the current sitemap;
- title or description length exceeds configured limits;
- an output is empty, duplicated, stuffed with keywords, or materially identical to the current text;
- it introduces numbers, dates, percentages, currencies, or factual entities absent from the supplied source text;
- it uses prohibited legal, tax, visa, ownership, price, yield, return, or guarantee language not already present in the source;
- its source-fragment list cannot be matched to the supplied page context;
- the API response is refused, incomplete, or fails schema parsing.

Validation is intentionally conservative. A rejected proposal is reported but does not fail the monitoring and reporting portions of the daily loop.

### Machine-owned override store

Validated proposals are upserted into `data/seo_content_overrides.json`, keyed by target URL and finding fingerprint. Each entry records:

- generated fields;
- base content hash;
- generation timestamp;
- model name;
- Search Console signal summary;
- lifecycle state;
- cooldown expiry.

`src/build_unified_app.py` applies only recognized fields to recognized pages. Unknown URLs, fields, or malformed entries fail the build. Generated artifacts remain derived output and are regenerated normally.

This file is the only model-influenced repository input in the first release.

### Draft pull-request orchestrator

The feedback loop collects all validated proposals from a run and opens one consolidated draft pull request. Its body includes:

- the source issues and fingerprints;
- before-and-after title, description, intro, FAQ, and link text;
- Search Console evidence for each target;
- validation results;
- explicit confirmation that no new factual claims were permitted;
- test and static-build results.

The pull request is labeled `implementation-queued`, `generated-content`, and `needs-human-review`. It is never marked `auto-merge-safe` and never passed to the existing auto-merge function.

After merge, the source issues receive `implemented-awaiting-google`. The existing feedback loop then suppresses duplicate work until Google supplies enough later data to validate or reject the result.

## Data Flow

1. The daily SEO monitor emits Search Console findings.
2. Existing classification and deduplication run unchanged.
3. Eligible existing-page findings are grouped, capped, and passed to the context collector.
4. The generator produces one structured proposal per finding.
5. The validator accepts or rejects each proposal independently.
6. Accepted proposals are applied to the override store on a generated branch.
7. The site is rebuilt and the full verification suite runs.
8. If there is a real diff and all checks pass, one draft pull request is opened.
9. Rejections and generator failures are added to the feedback-loop summary and control issue.
10. A merged draft deploys through the existing Pages workflow.

## Selection, Deduplication, and Rate Limits

- Preserve the current Search Console thresholds unless tests demonstrate a regression.
- Generate at most five editorial proposals per scheduled run.
- Prefer higher-impression findings, then better average position, then older unresolved findings.
- Do not regenerate a target with an open generated-content pull request.
- Do not regenerate findings labeled `implemented-awaiting-google`.
- Apply a 28-day target-page cooldown after merge unless a severe regression is detected.
- Skip a proposal when the base content hash changed after context collection.
- Keep one active generated proposal per canonical target URL.

## Failure Handling

- Missing `OPENAI_API_KEY`: skip generation, keep monitoring healthy, and report configuration status in issue #1.
- Transient API or network failure: retry up to three times with bounded backoff, then skip generation for that run.
- Refusal, incomplete response, schema failure, or policy rejection: record a concise reason and continue with other findings.
- Build or test failure: do not push the generated branch or open a pull request.
- GitHub branch or pull-request failure: leave the main branch unchanged and report the failure.
- A stale content hash aborts that proposal rather than attempting to merge competing edits.

No failure in content generation may prevent the Search Console report, status dashboard, control issue, or workflow artifacts from being updated.

## Testing

### Unit tests

- Context extraction for guide, country, destination, and homepage targets.
- Strict response parsing with a mocked OpenAI client.
- Validator acceptance and rejection for every prohibited claim category.
- Length, duplication, sitemap-link, source-fragment, number-introduction, and stale-hash checks.
- Override upsert behavior and malformed-entry rejection.
- Priority ordering, five-item cap, open-PR suppression, and cooldown behavior.

### Builder tests

- Each allowed override field changes only its intended rendered element.
- Unknown URLs and fields fail clearly.
- Empty and `null` fields preserve current content.
- FAQ schema matches the visible FAQ content.

### Integration tests

- A fixture report produces a deterministic override diff and draft-PR description without network access.
- A rejected proposal produces no repository diff.
- A mixed batch applies valid proposals and reports invalid ones.
- Full static generation, sitemap verification, tracking verification, and existing SEO content tests pass.

### Workflow validation

- A manual dry run verifies secret detection and mocked generation.
- A live manual run generates a draft pull request only.
- Merge and deployment are tested separately through the existing protected path.

## Repository and Workflow Changes

Expected implementation files:

- Add `scripts/seo_content_generator.py`.
- Add `data/seo_content_overrides.json`.
- Add focused generator, validator, and builder tests.
- Update `src/build_unified_app.py` to consume validated overrides.
- Update `scripts/seo_feedback_loop.py` to batch eligible findings and orchestrate draft pull requests.
- Update `.github/workflows/seo-feedback-loop.yml` to install the OpenAI Python SDK, expose `OPENAI_API_KEY`, and run generation without making it a prerequisite for monitoring.
- Update `docs/SEO_GROWTH_SYSTEM.md` with setup, guardrails, and recovery instructions.

## Required Configuration

GitHub Actions secret:

```text
OPENAI_API_KEY
```

Optional repository or workflow variable:

```text
SEO_CONTENT_MODEL=gpt-5.6
```

The API key must never be printed, placed in generated artifacts, added to pull-request content, or stored in the repository.

## Rollout

1. Ship the generator in dry-run mode with fixture-based validation.
2. Enable live API generation for one proposal per manual run.
3. Confirm two successful draft pull requests and their rendered previews.
4. Enable the scheduled flow with the five-proposal cap.
5. Review Search Console results after the 28-day cooldown before considering any scope expansion.

## Definition of Done

- A qualified existing-page finding produces a real content diff rather than a proposal-only document.
- The model output conforms to a strict schema and passes deterministic policy checks.
- The site rebuild and all verification tests pass.
- One consolidated draft pull request clearly shows before-and-after content.
- Editorial content cannot auto-merge or publish without approval.
- Unsupported factual claims are rejected.
- Duplicate and stale proposals are suppressed.
- Generation failures do not interrupt the daily SEO report.
- Merged changes enter the existing `implemented-awaiting-google` measurement loop.
