# Fukuoka / Itoshima editorial refresh review

**Review date:** 2026-08-23
**Scope:** property-evidence consolidation, reader-facing copy, and image variety

## Editorial acceptance

- One section titled **What homes cost** contains all three asking-price observations.
- Each property record includes its compatible official evidence as **Price context**; no second listing-like market-anchor section appears.
- Reader copy states price range, access, resale and buyer implications. Production commentary about dataset priority, rendering order, or exchange-rate handling is absent.
- The image set has three distinct roles: defining place, built environment and access, and decision texture.
- The new Itoshima decision-texture image contains no people and shows the road width, drainage, coastal exposure and housing context discussed in the article.

Follow-up review on 2026-08-23 renamed the benchmark to **Price context** and made its purpose explicit. Every record now states what the official evidence helps explain and what it cannot establish about the individual listing. Reader-facing capture dates and confidence labels were removed; the records now use direct listing actions where available and accurately label search-result links as source listings.

## Browser QA

| Check | Result |
| --- | --- |
| Mobile viewport | 390 × 844 |
| Mobile document client / scroll width | 390 / 390 |
| Mobile property-record client / scroll width | 362 / 362 for all three records |
| Desktop viewport | 1440 × 1000 |
| Desktop document client / scroll width | 1440 / 1440 |
| Desktop property-record client / scroll width | 830 / 830 for all three records |
| Page-origin console errors | 0 |
| Page-origin console warnings | 0 |
| Replacement image rendered size | 362 × 203.625 at mobile; source 1672 × 941 |

Mobile and desktop screenshots were inspected for field hierarchy, wrapping, captions, local-comparison placement, and image crop. No clipped content or duplicated evidence block was found.

## Automated verification

- Focused editorial, dossier and Japan-guide suite: **47 passed**.
- Full repository suite: **603 passed**.
- Production build: completed successfully from source.
- Intended source, test, documentation and Fukuoka artifact files have no staged/unstaged overlap. The full build refreshed unrelated generated pages in the isolated worktree; those unrelated outputs are excluded from this change.
