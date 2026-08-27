# Global Home Atlas Site-Wide Design System

**Date:** 2026-08-27  
**Status:** Proposed  
**Canonical references:** the current country retirement guides and premium destination dossiers, especially Japan and Fukuoka / Itoshima

## 1. Purpose

Global Home Atlas should feel like one publication even when a reader moves among an editorial country guide, an evidence-heavy destination dossier, a country hub, and an interactive comparison tool. The premium country and destination pages establish the brand standard: calm, informed, international, and useful to a Monocle-type reader. The rest of the site should inherit that standard without making every page use the same density or layout.

This work creates one shared visual foundation and three related presentation modes. It changes the site shell and presentation system, not the underlying research, scores, URLs, structured data, analytics, or application behavior.

## 2. Goals and non-goals

### Goals

- Give every public page the same recognizable header, footer, typography, palette, spacing rhythm, controls, link treatment, and trust language.
- Preserve the editorial restraint of the country guides: generous space, serif display type, regular-weight sans serif, fine rules, square controls, and minimal ornament.
- Preserve the destination dossiers' ability to communicate dense scores, property evidence, and comparisons without becoming visually academic or dashboard-like.
- Preserve the dashboard and calculators as efficient tools while making their brand expression consistent with the publication.
- Remove unnecessary duplication between template-specific CSS and markup.
- Make future templates start from shared primitives instead of copying a page-specific style block.
- Meet responsive, accessibility, and performance requirements across all page families.

### Non-goals

- Rewriting editorial content or changing the ten-dimension scoring model.
- Changing page URLs, canonical URLs, anchor IDs, page titles, schema, or sitemap behavior.
- Replacing the logo or commissioning a new brand identity.
- Introducing a JavaScript framework, CSS framework, external webfont dependency, or runtime asset service.
- Making the dashboard look like a magazine article or making articles look like the dashboard.
- Adding decorative badges, pills, gradients, shadows, metadata, or panels without a distinct reader purpose.

## 3. Design direction

### Chosen direction: one foundation, three modes

The implementation will use shared tokens and components with a page-level mode modifier.

1. **Editorial mode** — country retirement guides and long-form buying guides. It uses the widest editorial hierarchy, large serif headlines, warm paper, restrained rules, long-form reading measures, scenic photography, and an optional sticky contents rail.
2. **Dossier mode** — destination pages. It uses the same shell and typography but supports denser score, market, property, and diligence evidence. Tables and records remain plain and scannable; evidence is not converted into ornamental cards.
3. **Utility mode** — dashboard, Find Your Fit, calculators, shortlist tools, and other interactive products. It is sans-first and more compact. Serif is reserved for the page title or major section headings. Controls remain square, legible, and functional.

Country hubs, guide indexes, methodology, research standards, about, and similar index/trust pages use a **library variant** of the editorial mode: editorial shell and headings with concise lists, tables, and restrained panels.

### Alternatives considered

- **A global CSS overlay on the current templates** would be quick, but it would preserve duplicated navigation, page-specific specificity battles, and inconsistent semantics. Rejected.
- **A complete component-framework rewrite** could produce clean architecture, but it would add runtime and migration risk to a working static generator. Rejected.
- **A shared Python rendering and CSS module with staged template adoption** keeps static output, allows small testable changes, and directly removes the duplication found in the audit. Selected.

## 4. Visual foundation

### Color tokens

The system uses a small, named palette. Template CSS must consume these tokens rather than repeat hex values.

| Token | Value | Use |
| --- | --- | --- |
| `--gha-ink` | `#24312d` | Primary text, rules, dark controls, footer |
| `--gha-paper` | `#f4efe4` | Main editorial background |
| `--gha-surface` | `#fffdf7` | Deliberate raised or form surfaces |
| `--gha-muted` | `#68726d` | Secondary text and captions |
| `--gha-rule` | `rgba(36, 49, 45, .24)` | Dividers and table rules |
| `--gha-accent` | `#a44e2f` | Eyebrows, selected emphasis, focus companion |
| `--gha-link` | `#5f7f72` | Text links |
| `--gha-brass` | `#a98a4b` | Logo-adjacent or rare editorial accent |

Pure white, gradients, and shadows are not defaults. A white surface may be used when it improves form or data legibility. A shadow must communicate elevation, such as an open mobile menu; it is not decoration for ordinary sections.

### Typography

No remote font files are required. The system uses stable system stacks:

- Display serif: `"Iowan Old Style", Baskerville, "Palatino Linotype", Palatino, Georgia, serif`
- Reading/UI sans: `"Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif`

Weight rules are deliberate:

- Display headlines and section headings: `500`; `600` is allowed for small serif FAQ questions.
- Body copy: `400`; `500` only for useful inline emphasis.
- Navigation, eyebrows, bylines, captions, buttons, and table headings: `500` or `600`; never `800` or `900`.
- Data values may use `600` when needed for scanning; labels remain `500` or `600`.
- Destination names in prose are contextual links, normally `600`, with a restrained underline. They are not merely bold text.

Editorial body copy targets `17px` and `1.68–1.74` line height on desktop with a maximum readable measure of `72ch`. Utility copy may be `14–16px` with a minimum `1.45` line height. Text must not be made smaller than `12px` for captions or `14px` for interactive controls.

### Layout and spacing

- Global shell maximum: `1220px`.
- Desktop editorial content: article up to `830px`, rail `220px`, gap `48–112px` depending on viewport.
- Reading measure: no paragraph wider than `72ch`.
- Spacing scale: `8, 12, 16, 24, 32, 48, 72, 96px`.
- Editorial sections use whitespace and horizontal rules, not boxed cards.
- Dossier evidence may use tables, definition grids, and bordered records, but nested boxes are avoided.
- Utility pages may use restrained panels for real interaction or grouping. Maximum ordinary corner radius is `6px`; primary editorial controls remain square.
- Decorative pill navigation and repeated chip labels are prohibited. A horizontally scrollable mobile section navigator may use compact rectangular controls only when it materially aids navigation.

### Imagery

- Editorial and dossier hero imagery must show the destination's particular appeal rather than a generic lifestyle scene.
- Inline images should vary subject and scale: landscape, streetscape, architecture, market context, or daily-life detail. Repeated imagery of older people walking is specifically avoided.
- No hero montages. Use one strong hero image and distribute supporting images through the page.
- Figures use a consistent aspect ratio appropriate to context, `object-fit: cover`, and a plain descriptive caption.
- Captions identify place and reader-relevant appeal. They do not describe the research process.

## 5. Shared components and contracts

### Site header

There will be one semantic header renderer for every routed page. It must provide:

- the same logo, home link, five primary links, labels, order, and destinations;
- regular/medium navigation weight;
- a desktop link row and accessible native `details` mobile menu;
- a visible keyboard focus state;
- mode-aware colors without changing markup or information architecture;
- no duplicate primary navigation in the DOM outside the mobile alternative already required by the responsive menu.

The existing `primary_nav_html()` and `topbar_nav_html()` paths will converge on this renderer.

### Site footer

There will be one footer renderer with concise publication, trust, and utility links. Page-specific research caveats may precede it, but the footer itself must not accumulate repeated summaries or promotional copy.

### Hero

- Editorial: two-column text and scenic figure when an image exists; otherwise a text-led composition using the same spacing.
- Dossier: title, clear verdict or framing text, and a concise score/market summary; summary data must not be repeated immediately below.
- Utility: compact title, explanation, and the primary action or control context; no oversized editorial image that pushes the tool below the fold.
- Publication dates appear once in the byline/update line, not in a separate eyebrow plus byline.

### Content section

An editorial section is an unboxed block separated by spacing and a fine rule. A panel is allowed only for a form, interactive control, comparison, warning, or clearly bounded data group. Every repeated label or summary must provide new information.

### Links and buttons

- Text links are underlined and use the link token.
- Destination names in prose link to their destination dossiers when those pages exist.
- Primary buttons are dark ink with paper text, square or at most `2px` radius, and medium weight.
- Secondary actions are text links unless equal action priority is intentional.
- Button labels describe the action; they do not use vague process language.

### Tables and evidence records

- Tables use a dark top rule, fine row rules, no zebra striping by default, and internally scroll on narrow screens.
- Headings use medium-weight uppercase sans serif at a readable size.
- Dossier score explanations use **Atlas read** as the human-facing label.
- Property examples appear in one section only. Each example may include a listing image and direct listing link when available, plus price, size, buyer relevance, and a clearly explained local price context.
- Internal process metadata such as capture workflow, confidence labels, exchange-basis notes, or phrases such as “research inputs” do not appear in reader-facing records unless they materially qualify the evidence.

### Rail and mobile navigation

- Editorial and dossier pages may use one sticky contents rail at desktop widths.
- Rail text must be at least `14px`, regular or medium weight.
- The rail becomes an in-flow or compact section navigator on small screens; it must not cover content or require horizontal page scrolling.
- Rail calls to action and caveats appear once.

### Trust and update language

- Author, first-published date, and updated date share one plain, regular-weight line.
- References and source/update policy sit at the end of the article or dossier.
- Trust caveats are concise and reader-facing. They explain what must be independently verified, not the team's internal method.

## 6. Technical architecture

Create `src/site_design_system.py` as a dependency-free module of pure render and style functions. It will contain:

- `design_tokens_css()` — root variables and typographic stacks;
- `site_foundation_css()` — reset, shell, links, focus, responsive foundations;
- `site_components_css()` — header, footer, buttons, figures, tables, rail, and shared content primitives;
- `site_mode_css(mode)` — limited modifiers for `editorial`, `dossier`, `library`, and `utility`;
- `site_header_html(css_prefix="gha")` — one header contract;
- `site_footer_html(css_prefix="gha", caveat=None)` — one footer contract;
- small pure helpers only where markup is genuinely shared.

`src/build_unified_app.py` remains the content and routing builder. It imports the shared module and supplies page-specific content. Existing template class names may remain temporarily behind compatibility selectors during migration, but new shared elements use a `gha-` prefix. Compatibility selectors must be removed in the phase that completes their template family's migration.

The generated site remains static HTML and CSS. No runtime fetch, hydration, build-time network request, or third-party dependency is introduced.

## 7. Migration sequence

The initiative is delivered in independently deployable batches so a visual regression can be isolated and reversed without holding the whole site.

### Batch 1 — foundation and editorial pages

- Add the shared module and its tests.
- Migrate the country retirement guides and other SEO/editorial guides.
- Replace duplicated Japan and general retirement-guide CSS with one editorial mode.
- Migrate shared header/footer markup for this family.
- Verify Japan, Spain, and one newly upgraded country guide at desktop, tablet, and mobile widths.

### Batch 2 — premium destination dossiers

- Apply the dossier mode to all premium dossier pages.
- Preserve the ten-dimension assessment, property examples, location guidance, checklist, and references.
- Remove residual duplicate summaries, internal process language, and inconsistent source styling.
- Verify Fukuoka / Itoshima plus urban, resort, island, and alpine examples.

### Batch 3 — hubs, trust pages, and guide indexes

- Migrate country hubs, guide hub, methodology, research standards, about, comparison, and report-library pages to the library mode.
- Replace decorative card grids with lists, tables, or simple bordered groups where the card does not communicate an independent unit.

### Batch 4 — tools and dashboard

- Migrate dashboard, Find Your Fit, retirement calculator, shortlist review, landing page, and other interactive pages to utility mode.
- Preserve control density, filtering, calculations, chart legibility, tracking attributes, and keyboard behavior.
- Use the common header/footer and visual tokens without forcing editorial page proportions onto tools.

Each batch receives its own test-first implementation plan, review, and deploy check. Later batches start only after the prior batch is stable in production.

## 8. Behavior and data preservation

The migration must preserve:

- routes, trailing-slash behavior, canonical links, titles, descriptions, schema, breadcrumbs, sitemap inclusion, and internal-link destinations;
- all destination scores, weights, evidence, listing data, calculator formulas, dashboard filters, shortlist state, and country-guide content;
- element IDs used by anchors or scripts;
- analytics attributes and event names;
- native disclosure behavior and form semantics;
- existing image sources and alt text unless an explicit image-quality task changes them.

When markup must change for shared components, tests must demonstrate equivalence for these contracts.

## 9. Testing strategy

Implementation follows red–green–refactor. Before a shared component or page family changes, a failing contract test is added.

### Automated contracts

Add `tests/test_site_design_system.py` and extend focused template tests to assert:

- all routed pages expose the same primary desktop navigation and accessible mobile navigation;
- every rendered page has exactly one recognized design mode on `body`;
- shared token, header, and footer CSS is emitted once per page;
- representative pages from every mode contain the expected shared components;
- navigation/byline/eyebrow/button styles do not regress to `800` or `900` weights;
- tables are inside responsive wrappers;
- destinations named in editorial prose retain valid dossier links;
- IDs, analytics attributes, schemas, and functional form/control markup remain present;
- page generation produces no broken internal asset paths.

The existing navigation-consistency test remains a site-wide guard. The full unit suite and static build run after every batch.

### Visual QA matrix

For every batch, render representative pages at:

- `1440 × 1200` desktop;
- `1024 × 900` tablet/small desktop;
- `390 × 844` mobile.

Check header alignment, line length, hierarchy, image cropping, captions, rail behavior, table overflow, form controls, focus states, footer consistency, and absence of page-level horizontal overflow. Batch 2 additionally samples urban, coastal, alpine, island, and resort dossiers. Batch 4 exercises actual filtering and calculator flows rather than checking screenshots alone.

### Performance and accessibility

- No new network dependency or client framework.
- No page-level horizontal overflow at widths from `320px` upward.
- Interactive targets are at least `42px` high on mobile.
- Text and control contrast meet WCAG AA.
- Keyboard focus is visible and not conveyed by color alone.
- Heading order, landmark labels, figure captions, table headers, form labels, and native disclosure semantics remain valid.
- Images keep explicit dimensions or aspect-ratio reservations to limit layout shift.

## 10. Acceptance criteria

The initiative is complete when:

1. Every routed public page uses the shared header, footer, tokens, and one defined mode.
2. Country guides visually match the approved premium editorial standard without duplicated Japan-only styling.
3. Every premium destination page uses the approved dossier standard and retains one useful property-evidence section.
4. Hubs and trust pages feel editorially related without unnecessary decorative cards.
5. Dashboard and tools remain fast and task-oriented while visibly belonging to Global Home Atlas.
6. No reader-facing copy describes internal research or publishing process unless it is necessary evidence qualification.
7. The full automated suite and build pass, and the responsive visual QA matrix shows no material regressions.
8. Production smoke checks return successful responses for representative pages in all modes after each deployment.

## 11. Risks and mitigations

- **CSS specificity regressions:** migrate by family, use the `gha-` namespace, and delete compatibility selectors at the end of each batch.
- **A visually consistent but less usable dashboard:** keep utility density and interaction tests separate from editorial acceptance checks.
- **Large generated HTML diffs:** isolate shared shell changes from content changes and review representative artifacts before applying family-wide.
- **Hidden mobile overflow in tables or rails:** require internal table scrolling and test the complete `320–1024px` range.
- **Repeated metadata returning through old helpers:** centralize byline, trust, header, footer, and property-record contracts and assert occurrence counts.
- **Future template drift:** document mode selection and require new routed pages to use the shared module in tests.
