# Landing Page Design-System Pilot Implementation Plan

> **Execution scope:** Apply the approved site-wide design system to the root landing page only. Stop after verification and deployment for user confirmation before changing any other template family.

**Goal:** Make the Global Home Atlas landing page a production-quality preview of the shared premium visual system while preserving its existing content, navigation, finder behavior, links, tracking, metadata, and structured data.

**Architecture:** Add a dependency-free `src/site_design_system.py` containing shared visual tokens and semantic header/footer renderers. `build_landing_page()` will consume those primitives and retain its current content/data helpers and finder script. The landing page receives a single `gha-mode-landing` body modifier and a restrained hybrid layout: editorial hierarchy and whitespace around a compact utility finder.

**Technology:** Python standard-library static generator, inline generated CSS, `unittest`, Playwright/browser rendering for visual QA.

---

## Task 1: Lock the landing-page design contract

**Files:**
- Create: `tests/test_site_design_system.py`
- Modify: `tests/test_seo_ctr_content.py`

1. Add failing tests requiring one `gha-mode-landing` body class, one shared primary header, one shared footer, and shared token CSS.
2. Add failing typography tests prohibiting `800`, `850`, or `900` weights on landing navigation, eyebrows, buttons, captions, and metadata.
3. Add failing structure tests requiring unboxed primary sections, square primary controls, the existing finder IDs, existing conversion and recommendation links, and all current analytics markers.
4. Run the two focused test modules and confirm the new assertions fail for the expected missing contracts.

## Task 2: Create the shared design-system module

**Files:**
- Create: `src/site_design_system.py`
- Modify: `src/build_unified_app.py`
- Test: `tests/test_site_design_system.py`

1. Implement pure helpers for design tokens, foundation/component CSS, landing-mode CSS, primary header HTML, and footer HTML.
2. Reuse the established primary navigation destinations and labels without introducing an import cycle; pass the link collection and site metadata into renderer functions.
3. Use `gha-` namespaced classes and visible focus styles.
4. Keep the output static, dependency-free, and free of external font requests.
5. Run the focused design-system tests until they pass.

## Task 3: Migrate only the landing-page shell and hierarchy

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_seo_ctr_content.py`

1. Replace the landing page's duplicate root variables, topbar, generic footer, and base component styles with the shared module output.
2. Add `class="gha-mode-landing"` to the body and use the shared header/footer renderers.
3. Restyle the hero to use the approved serif/sans hierarchy, medium weights, square actions, editorial rules, and a single scenic visual treatment.
4. Convert generic card-box sections to rule-separated editorial groups. Keep panels only for the working market finder, destination recommendations, and final conversion action where bounded grouping is useful.
5. Preserve section order and all content helpers. Do not rewrite copy during this visual pilot.
6. Keep the finder compact and usable: all existing IDs, select behavior, dynamically rendered result links, and tracking calls remain unchanged.
7. Run focused landing tests until green.

## Task 4: Verify behavior, accessibility, and responsive output

**Files:**
- Modify only if a failing check exposes a defect in the pilot files above.

1. Run `python3 -m unittest tests.test_site_design_system tests.test_seo_ctr_content tests.test_find_your_fit_page tests.test_navigation_consistency`.
2. Build the site with the repository's standard build command.
3. Run the complete `python3 -m unittest discover -s tests -p 'test_*.py'` suite.
4. Serve the generated artifacts locally and inspect `/` at `1440 × 1200`, `1024 × 900`, and `390 × 844`.
5. Verify no horizontal page overflow, visible keyboard focus, mobile menu usability, readable finder controls, intact destination images, and no repeated or process-oriented metadata.
6. Exercise the market finder and its primary links in the browser.
7. Review the generated diff to confirm no non-landing page HTML or source content was intentionally changed.

## Task 5: Independent review, deploy, and stop

**Files:**
- Modify only for defects found during review.

1. Review the implementation against the approved specification and the minimal-artifact rule.
2. Re-run focused tests, the full suite, build, and production-oriented smoke checks after any correction.
3. Commit the pilot, push the branch, open and merge its PR, then verify the production homepage returns `200` and contains the landing design-mode marker.
4. Provide the production URL for visual review.
5. Stop. Do not begin Batch 1 or modify other page families until the user explicitly confirms the pilot.
