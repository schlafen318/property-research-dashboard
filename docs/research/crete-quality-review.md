# Crete destination dossier quality review

Reviewed: 2026-08-22

## Result

**100/100 — publish-ready.**

| Gate | Points | Result |
|---|---:|---|
| Decision usefulness and local specificity | 20/20 | The verdict and five lenses distinguish Chania / Akrotiri, Apokoronas, Rethymno, Heraklion, Agios Nikolaos / Elounda and the wider Lasithi case instead of averaging Crete into one market. |
| Ten-factor assessment | 15/15 | All ten canonical scores appear once, retain the underlying destination data and use concise local Atlas reads. |
| Legal, tax, rental and risk accuracy | 15/15 | Residence is separated from ownership; AFM, transfer tax, cadastral and planning diligence, rental registration, healthcare and climate claims are bounded and linked to authoritative Greek sources. |
| Market evidence and representative listings | 15/15 | Three July 2026 asking-price anchors sit beside three current direct residential observations spanning Apokoronas, Rethymno and Agios Nikolaos, with explicit asking-evidence limitations. |
| Structure and editorial clarity | 10/10 | The page follows the shared premium sequence, keeps references last, removes the generic accordion treatment and uses direct decision language. |
| Visual system and original imagery | 10/10 | Three separate original images establish Chania's working-city identity, Apokoronas daily life and eastern-Crete heat and water operations without a montage or resort-advertising treatment. |
| Accessibility and responsive behaviour | 10/10 | Semantic headings, descriptive alt text, contained tables and a visible mobile menu pass desktop and exact 390×844 review with no document overflow. |
| Verification and maintainability | 5/5 | Evidence ledger, recheck triggers, 11 targeted contract tests, full 446-test regression suite, compile checks and a clean browser console are in place. |

## Verification record

- `python3 -m unittest tests.test_crete_premium_dossier`: 11 passed.
- `python3 -m unittest discover -s tests -p 'test_*premium_dossier.py'`: 133 passed.
- `python3 -m unittest discover -s tests`: 446 passed.
- `python3 src/build_unified_app.py`: completed.
- Python compile checks: passed.
- Desktop browser review: passed; hierarchy, rail, imagery and all decision modules render correctly.
- Exact 390×844 browser review: 390 px document width, no horizontal page overflow; score, listing and location tables remain contained or intentionally scroll inside their wrappers.
- Browser console: zero messages.
- Final source images: original WebP assets, visually inspected after conversion.

This rating applies to the reviewed edition and dated evidence. Any material residence, tax, cadastral, licensing, airport, healthcare, hazard, water, insurance, listing or market-data change requires re-review.
