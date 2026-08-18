# First-Impression Recovery Design

## Objective

Automatically create a reviewable generated-content proposal when a tracked page is indexed but still has zero Search Console impressions after its first-impression deadline. Start with the retirement guide, limit recovery to one page per SEO run, and preserve every existing content-safety and cooldown control.

## Eligibility

A finding is eligible only when all of these conditions hold:

- It is a `seo-goal-missed` finding for the `impression_status` goal.
- The page's `index_status` is `met`.
- Search Console reports zero impressions.
- The target is supported by the existing content renderer and appears in the sitemap.
- The source issue is not labeled `implemented-awaiting-google`.
- No generated-content PR is already open for the target.
- No active override or merged generated-content PR places the target in its 28-day cooldown.

Indexing misses and impression goals that are merely at risk are never generation candidates.

## Selection

First-impression recovery has priority over ordinary CTR and near-ranking generation because it represents a missed high-severity goal. A run selects at most one recovery target and creates one draft PR for that page. Guide pages rank ahead of country hubs, which makes `buying-property-abroad-for-retirement` the first current target; ties are deterministic by canonical URL and fingerprint.

If no recovery page is eligible, the existing generated-content selection behavior remains unchanged.

## Data Flow

Classification adds explicit machine fields to an eligible goal finding:

- `goal_field: impression_status`
- `recovery_type: first-impression`
- `page: <canonical URL>`
- `impressions: 0`

The finding is marked as an implementation candidate but does not create the older implementation-queue scaffold. It enters only the existing generated-content pipeline. That pipeline collects canonical rendered context, calls the configured model, validates every proposal deterministically, writes a content override, rebuilds and verifies the site, and opens a draft PR.

The model receives the current page intent and the zero-impression recovery signal. It may propose title, meta description, intro, FAQ, and internal-link changes already supported by the existing schema. It receives no authority to invent claims or expand the protected-topic policy.

## Lifecycle

After a generated-content PR merges, the existing reconciliation adds `implemented-awaiting-google` to the source issue. That prevents another recovery proposal until Search Console supplies new evidence. Existing stale-signal, goal-status, open-PR, and cooldown reconciliation remain authoritative.

Dry runs report the selected recovery candidate without calling the model or mutating GitHub.

## Failure Handling

Unsupported targets, stale page hashes, model refusals, validation failures, build failures, and GitHub failures continue through the current generated-content rejection and error paths. A failure must not create an override, push a misleading branch, label the issue as implemented, or block later daily runs.

## Verification

Tests must prove:

- An indexed, missed first-impression goal becomes a generated-content candidate.
- Indexing misses, at-risk impression goals, and non-indexed pages do not become recovery candidates.
- Recovery selection chooses the retirement guide before country hubs and returns only one recovery page.
- Open PR, `implemented-awaiting-google`, and cooldown suppression still apply.
- With no eligible recovery, ordinary generated-content prioritization remains unchanged.
- The main dry-run orchestration routes the selected recovery through the generated-content scaffold without creating an implementation-queue PR.
- The full unit suite, compilation, static-site verification, tracking verification, and diff check pass.
