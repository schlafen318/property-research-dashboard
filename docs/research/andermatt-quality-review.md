# Andermatt quality review

Independent reviewer: Codex independent reviewer (`queenstown_review`)
Approval date: 2026-08-25
Result: 100/100 — publish-ready locally

| Canonical scorecard | Weight | Score |
|---|---:|---:|
| A. Decision usefulness | 15 | 15 |
| B. Evidence and claim discipline | 25 | 25 |
| C. Atlas model and narrative alignment | 15 | 15 |
| D. Property evidence and market context | 15 | 15 |
| E. Editorial quality | 10 | 10 |
| F. Design and responsive presentation | 10 | 10 |
| G. SEO and research handoff | 5 | 5 |
| H. Build integrity and maintenance | 5 | 5 |

## Verification evidence

- Static build: `python3 src/build_unified_app.py` completed on 2026-08-25.
- Mobile QA: exact 390×844 viewport; document width 390/390 and both responsive record wrappers 362/362, with no horizontal overflow. Screenshot: `output/playwright/andermatt-390x844.png`.
- Desktop QA: exact 1440×1000 viewport; document width 1440/1440 and both record wrappers 830/830, with no horizontal overflow. Screenshot: `output/playwright/andermatt-1440x1000.png`.
- Visual review: premium hierarchy, readable lede and navigation, coherent single-scene hero, no clipping or overlap at either viewport.
- page-origin warnings/errors: 0 at both viewports, measured with Playwright CLI.
- Images: all three distinct Andermatt assets loaded at 1672×941; source-output paths and publication rights are recorded in the provenance file.
- Focused suite before approval: 8/9 passed; the sole failure was the intentionally withheld independent-approval record.
- Full-suite baseline before the Andermatt candidate: 655/655 passed.
- Independent review: canonical 100/100 approved on 2026-08-25 with no Critical, Important or Minor findings.
- Final focused suite after approval: 9/9 passed on 2026-08-25.
- Final full suite after approval: 664/664 passed on 2026-08-25.
