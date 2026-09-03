# Human-Readable Market Pages

## Purpose

Make destination profiles and the all-markets directory easier for a human reader to scan, understand, and act on. The redesign removes repeated labels, controls, calls to action, and supporting links while preserving the underlying research and comparison capabilities.

## Design principles

- Put the reader's next decision first.
- Show each fact once in the most useful location.
- Use plain labels: “Overall rating” instead of “Decision score,” and “Price guide” instead of “Entry benchmark.”
- Prefer whitespace and typographic hierarchy over nested cards, chips, badges, and repeated headings.
- Keep advanced research tools available through progressive disclosure.
- Use the same information hierarchy across all destination profiles.

## Destination profiles

### Hero

- Use the destination name alone as the visible `h1`, such as “Dubai.”
- Keep the document title descriptive for search results, but remove “Property Research” from the visible heading.
- Show category and country in the eyebrow without an updated date.
- Present three concise hero facts: global rank, overall rating, and price guide.
- Preserve the destination image and restrained visual treatment.

### At-a-glance summary

Replace the large “Should this destination stay on your shortlist?” decision panel with one compact summary.

The summary contains:

- A short verdict written as a direct editorial assessment.
- Best for.
- Ownership route.
- Price guide.
- Expected net yield.
- Main risk.

Each fact appears once. Do not restate the global rank or overall rating in this summary.

### Reading path

Use six section links:

1. Overview
2. Buyer fit
3. Areas
4. Costs and risks
5. Evidence
6. Compare

Existing research content can remain, but adjacent sections that answer the same question should be consolidated. Section introductions should be short and should not repeat the hero or at-a-glance verdict.

### Actions and supporting links

- Keep one compare/shortlist action area on the page.
- Remove the resource-heavy right sidebar.
- Move related destinations, country guides, buying guides, methodology, research standards, About, and Contact into one “Continue your research” section near the end.
- Show the last-updated date in a quiet line at the bottom of the page.

## Markets directory

### Default view

- Use “Markets” as the only page heading and remove the repeated inner “Markets” heading.
- Follow it with one short sentence explaining what can be compared.
- Show one primary filter row containing Search, Location type, Sort, and Buying goal.
- Default market rows show:
  - Market and country
  - Overall rating
  - Price guide
  - Expected net yield
  - Ownership clarity
- Omit normal “Available” buyer-access labels. Display a clear warning only when access is restricted.
- Make the market name the only default row action.

### Compare mode

- A single “Compare markets” control activates row-selection checkboxes.
- Once at least one market is selected, show one selection bar with the count and relevant compare, save, clear, and export actions.
- Do not render a permanent Compare and Shortlist control on every row.
- Limit comparison to four markets as in the existing behavior.

### Advanced tools

- Move score weighting, data export, saved-market management, and saved-preview content into one collapsed “Advanced research tools” section below the directory.
- Do not show empty saved-preview or saved-market cards in the default view.

### Responsive behavior

- Keep a compact table at larger widths.
- Render each market as a readable card at small widths.
- Preserve the same fact order across desktop and mobile.
- Avoid horizontal scrolling for the default market directory.

## Shared vocabulary

Use these labels consistently across destination profiles and the markets directory:

- Overall rating
- Price guide
- Expected net yield
- Ownership clarity
- Global rank
- Main risk

## Accessibility

- Preserve semantic headings, navigation labels, tables, buttons, and form labels.
- Compare mode must expose its expanded state and selected count to assistive technology.
- Restricted-access warnings must not rely on color alone.
- Focus styles remain visible for all interactive controls.

## Implementation boundaries

- Update the shared destination-page generator and markets-directory template.
- Preserve destination data, ranking logic, filtering, sorting, comparison calculations, saved-state behavior, analytics events, and SEO metadata unless a visible label or layout requires a direct change.
- Do not add new country pages, research sections, scoring dimensions, or marketing calls to action.
- Preserve the canonical top navigation established across the site.

## Verification

- Add failing tests for the destination title, updated-date placement, plain-language labels, consolidated supporting links, compact section navigation, and removal of the trust sidebar.
- Add failing tests for the single markets heading, default columns, restricted-only access warning, compare-mode controls, removal of repeated row actions, and collapsed advanced tools.
- Regenerate the full static site.
- Run the complete unit suite and static-site verifier sequentially.
- Check representative destination and markets pages at desktop and mobile widths for reading order, overflow, focus visibility, and browser errors.
