# Spain Retirement Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a Spain retirement-property guide that meets the Country Retirement Guide Standard and the editorial quality of the Japan reference article.

**Architecture:** Extend the existing SEO-page generator with a reusable editorial-retirement-guide path instead of adding a second country-specific fork. Store Spain's page metadata, narrative sections, destination guidance, references, rail navigation and image specifications as guide configuration consumed by shared rendering helpers.

**Tech Stack:** Python static-site generator, `unittest`, generated HTML/CSS, WebP editorial assets, GitHub Pages.

**Spec:** The approved Country Retirement Guide Standard in the current task, using the Japan article as the rendered reference.

## Global Constraints

- Residency and property ownership must be explicitly separated in the opening section.
- Legal and administrative claims must link to current official Spanish, EU, tax-agency, health-service, land-registry or BOE sources.
- National, autonomous-community, municipal and community-of-owners rental rules must not be conflated.
- The 2025 end of investor residence and the 2026 Supreme Court annulment affecting the national short-rental register must be described with dates and current-status caveats.
- Use one hero image and distribute two supporting images beside the sections they support; no montage.
- Consolidate Valencia, Málaga/Costa del Sol, Costa Brava/Girona and Mallorca into one destination-comparison table.
- References and update policy must be the final article section.
- Preserve the restrained editorial typography, regular-weight metadata and responsive reading layout established by the Japan guide.

---

### Task 1: Define the Spain guide contract with failing tests

**Files:**
- Create: `tests/test_spain_retirement_article.py`
- Modify: none
- Test: `tests/test_spain_retirement_article.py`

**Interfaces:**
- Consumes: `build_unified_app.SEO_PAGES`, `build_unified_app.build_seo_page()`
- Produces: executable requirements for the Spain page slug, article order, sources, destination table, imagery, metadata and responsive editorial layout

- [ ] **Step 1: Write the failing tests**

```python
def test_article_leads_with_residency_and_ended_investor_route():
    html = rendered_article()
    assert html.index("Buying property does not give you residency") < html.index('id="comparison"')
    assert "ended on 3 April 2025" in html
    assert "https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx" in html

def test_article_uses_one_consolidated_four_destination_table():
    html = rendered_article()
    assert html.count("Four Spanish destinations to compare") == 1
    for name in ("Valencia", "Málaga / Costa del Sol", "Costa Brava / Girona", "Mallorca"):
        assert name in html
```

- [ ] **Step 2: Run the test to verify RED**

Run: `python3 -m unittest tests.test_spain_retirement_article`

Expected: FAIL because the Spain retirement page does not exist.

- [ ] **Step 3: Add the remaining contract tests**

Cover healthcare, tax residence, non-resident property tax, buyer withholding on a non-resident seller, registry diligence, flood mapping, short-rental rule changes, final references, FAQ consistency, article schema, three distributed images and complete guide-rail links.

- [ ] **Step 4: Re-run RED**

Run: `python3 -m unittest tests.test_spain_retirement_article`

Expected: FAIL only for missing Spain-guide behavior.

### Task 2: Add reusable editorial-retirement rendering and Spain content

**Files:**
- Modify: `src/build_unified_app.py`
- Test: `tests/test_spain_retirement_article.py`

**Interfaces:**
- Consumes: `page["editorial_guide"]`, selected destination records, existing `destination_editorial_figure_html()`
- Produces: `is_editorial_retirement_guide(page)`, shared editorial body class, hero, guide rail and country-specific article sections

- [ ] **Step 1: Add Spain page metadata**

Create `spain-retirement-property-foreign-buyers` with the four existing Spain destination IDs, research-team author, publication date `2026-08-21`, retirement intent and four visible FAQs.

- [ ] **Step 2: Generalize the Japan-only presentation checks**

Replace Japan-only branching with an editorial-guide flag while retaining country-specific content configuration. Japan must render identically after the refactor.

- [ ] **Step 3: Write the Spain decision sequence**

Render, in order: residency first; who Spain suits; 2025–2026 rule changes; financing and ownership costs; retirement practicality; five retirement lenses; retirement-capital prompt; one destination table; related guides; FAQ; references.

- [ ] **Step 4: Add the official sources**

Use the Ministry of Inclusion non-lucrative residence page, La Moncloa investor-residence notice, Agencia Tributaria residence and non-resident property pages, Social Security healthcare entitlement, Registradores buying/registry guidance, MITECO flood maps, BOE tourist-rental/community approvals and 2026 Supreme Court decisions, Aena access pages and 2025 Registradores market statistics.

- [ ] **Step 5: Run GREEN verification**

Run: `python3 -m unittest tests.test_spain_retirement_article tests.test_japan_retirement_article`

Expected: all Spain and Japan editorial-guide tests pass.

### Task 3: Generate and install Spain editorial imagery

**Files:**
- Create: `src/site_assets/spain-valencia-coast-hero.webp`
- Create: `src/site_assets/spain-malaga-daily-life.webp`
- Create: `src/site_assets/spain-mallorca-access-lifestyle.webp`
- Modify: `src/build_unified_app.py`
- Test: `tests/test_spain_retirement_article.py`

**Interfaces:**
- Consumes: three photorealistic-natural image prompts with no text, logo or watermark
- Produces: one portrait-compatible hero and two 16:9 supporting images referenced exactly once each

- [ ] **Step 1: Generate the Valencia hero**

Create an elevated Mediterranean view connecting Valencia's urban fabric, green public realm and coast in natural late-afternoon light; editorial travel photography, realistic texture, no fantasy landmarks.

- [ ] **Step 2: Generate Málaga daily life**

Create a candid, lived-in Andalusian neighborhood scene with shade, mature residents, café life and sea proximity; avoid resort-advertising gloss.

- [ ] **Step 3: Generate Mallorca lifestyle and access**

Create a calm coastal-town scene that shows premium island appeal and practical year-round settlement rather than an isolated beach.

- [ ] **Step 4: Inspect, convert and install**

Inspect each output, crop without distorting focal points, convert to WebP, copy into `src/site_assets`, and rebuild so deployment copies them into `artifacts/assets`.

- [ ] **Step 5: Run the image contract test**

Run: `python3 -m unittest tests.test_spain_retirement_article`

Expected: the hero appears before `</header>` and supporting images appear only inside their relevant lenses.

### Task 4: Build and visually verify

**Files:**
- Modify only if visual defects are found: `src/build_unified_app.py`
- Test: full test suite and rendered article

**Interfaces:**
- Consumes: completed generator and installed assets
- Produces: responsive static Spain article in `artifacts/spain-retirement-property-foreign-buyers/index.html`

- [ ] **Step 1: Run the full automated suite**

Run: `python3 -m unittest discover -s tests`

Expected: zero failures.

- [ ] **Step 2: Build the static site**

Run: `python3 src/build_unified_app.py`

Expected: successful build and Spain article emitted.

- [ ] **Step 3: Perform desktop visual QA**

Review at `1453x1237`: hierarchy, image crops, rail completeness, line length, table readability, references at end and absence of bold metadata.

- [ ] **Step 4: Perform mobile visual QA**

Review at `390x844`: menu, title wrapping, full-width imagery, body size, section rhythm, table scrolling and link wrapping.

- [ ] **Step 5: Run final cleanliness checks**

Run: `git diff --check`

Expected: no whitespace errors.

### Task 5: Publish and verify production

**Files:**
- Commit only source, tests, plan and source assets; do not commit generated `artifacts` output.

**Interfaces:**
- Consumes: verified branch
- Produces: merged pull request and public Spain article

- [ ] **Step 1: Commit and push**

Commit the reusable guide rendering, Spain content, tests and image assets on a `codex/` branch.

- [ ] **Step 2: Create the pull request and monitor checks**

Require all repository checks to pass before merge.

- [ ] **Step 3: Merge and monitor GitHub Pages deployment**

Wait for build, deploy and sitemap-notification jobs to complete successfully.

- [ ] **Step 4: Verify the live page**

Confirm the public HTML contains all three assets, final references, Article schema and no montage markup; load the live page in the in-app browser for review.
