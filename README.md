# Holiday & Retirement Property Destination Research Dashboard

This project packages the current property-development research into a Codex-ready workspace.

## Current outputs

- `artifacts/unified_destination_dashboard.html`  
  Self-contained mobile-first dashboard generated from `data/destinations.json`,
  `data/listings.json`, and `data/fx_rates.json`. This is the current combined
  app artifact for scorecards plus representative real listings.

- `artifacts/dashboard_mobile_first_v10.html`  
  Mobile-first interactive dashboard with 25 destinations, category scoring, judge-style verdicts, ownership/rental/yield/price notes, and FX assumptions.

- `artifacts/listings_appendix_usd.html`  
  Representative real listings appendix with 3 listing examples per destination, headline prices converted to USD, original local prices retained, and USD/m² where size is available.

- `artifacts/legacy_scorecard.xlsx`  
  Earlier spreadsheet version of the scorecard. Useful as a cross-check, but the unified HTML dashboard is the current canonical user-facing format.

## Source files

- `src/build_unified_app.py`  
  Builds the combined self-contained dashboard from the structured JSON data.

- `src/extract_data_from_artifacts.py`  
  Extracts dashboard and listing data from the existing HTML/script artifacts into structured JSON files.

- `src/create_listings_appendix.py`  
  Original script that generated the listings appendix from manually curated representative listing examples.

- `src/create_listings_appendix_usd.py`  
  Script that converts listings into USD headline prices and outputs the current USD appendix.

## Main objective

Continue improving the property-destination research product. The end-state should be a clean, mobile-friendly, investor-grade dashboard that compares global holiday/retirement development destinations on:

- Lifestyle and scenery
- Airport and business-centre access
- Ownership clarity for foreigners / Chinese buyers
- Short-term-rental and long-stay economics
- Latest property price in USD/m²
- Food quality and standard of living
- Retirement suitability
- Capital appreciation and exit liquidity
- Climate/regulatory/development risks
- Representative real listings

## Current universe

25 destinations are covered:

1. Fukuoka / Itoshima
2. Valencia
3. Algarve / Cascais
4. Málaga / Costa del Sol
5. Lake Como
6. Hakone / Izu
7. Madeira
8. Costa Brava / Girona
9. Hakuba
10. Crete
11. Annecy
12. Dolomites / South Tyrol
13. Da Nang / Hoi An
14. Queenstown
15. Niseko
16. Croatia / Istria-Dalmatia
17. Phuket / Samui
18. Bali
19. Mallorca
20. Innsbruck / Tyrol
21. Ticino / Lake Lugano
22. Chamonix
23. Andermatt
24. Whistler
25. Swiss Valais / Vaud Alps

## How to use in Codex

1. Open this folder in Codex.
2. Start with `docs/CODEX_PROJECT_BRIEF.md`.
3. Use `docs/NEXT_AGENT_PROMPT.md` as the direct prompt for a coding/research agent.
4. Treat `artifacts/unified_destination_dashboard.html` as the current combined app.
5. Treat `artifacts/dashboard_mobile_first_v10.html` and `artifacts/listings_appendix_usd.html` as legacy source artifacts.

## Build

The unified dashboard builder uses only the Python standard library:

```bash
python3 src/build_unified_app.py
```

Open `artifacts/unified_destination_dashboard.html` in a browser.

Optional production configuration is read from environment variables during the
static build:

```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX \
BING_SITE_VERIFICATION=YOUR_BING_META_VALUE \
CONTACT_EMAIL=hello@globalhomeatlas.com \
python3 src/build_unified_app.py
```

If `GA4_MEASUREMENT_ID` is omitted, the site still records first-party event
payloads into browser `localStorage` under `gha_event_queue`; once the GA4 ID is
provided, the same events are also sent through `gtag`.

Tracked events include dashboard opens, guide clicks, destination clicks,
comparison selections, memo shortlist additions/removals, memo export, JSON/CSV
exports, outbound listing clicks, and custom shortlist submissions.

## SEO Monitoring

Generate a Search Console report from the live sitemap and ignored local OAuth
token:

```bash
python3 scripts/seo_monitor.py --write
```

The report writes to `output/seo/` and includes sitemap URL counts, sitemap
submission status, top queries, top pages, and pages with impressions but low
CTR. The script reads `tmp/globalhomeatlas-google-token.json` when available;
`tmp/` and `output/` are intentionally ignored.

## Publish

The production entrypoint is generated at `artifacts/index.html`.

For GitHub Pages:

1. Push this folder to a GitHub repository with `main` as the default branch.
2. In the repository settings, set Pages source to GitHub Actions.
3. Run the `Deploy static dashboard` workflow, or push to `main`.

The workflow rebuilds the dashboard and publishes the `artifacts` directory.

## Important data caveats

- The data is research-grade, not transaction advice.
- Listing prices and availability change quickly.
- Some destination price benchmarks use city/resort averages, while others use listing samples or prime-market data.
- Yield figures are not perfectly comparable across countries because public sources mix STR revenue, gross residential yield, agent claims, and underwriting estimates.
- Any production version should show source dates, confidence levels, and update timestamps.

## Recommended next build

Continue hardening the unified HTML app:

- Source notes and confidence levels
- Editable weights
- Export/share capability
