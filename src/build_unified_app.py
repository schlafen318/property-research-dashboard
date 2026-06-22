from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
SITE_NAME = "Global Home Atlas"
SITE_URL = "https://globalhomeatlas.com/"
SITE_DESCRIPTION = (
    "Compare global home and property investment destinations with decision scores, "
    "ownership clarity, lifestyle fit, yields, and representative market evidence."
)

DIMENSIONS = [
    {
        "key": "lifestyle_magnetism",
        "label": "Lifestyle magnetism",
        "weight": 0.10,
        "sources": ["scenery", "year_round_activity", "food_quality"],
        "evidence": "Natural setting, food culture, and repeatable year-round reasons to be there.",
    },
    {
        "key": "global_access",
        "label": "Global access",
        "weight": 0.10,
        "sources": ["airport_access", "business_hub_access"],
        "evidence": "Airport quality, regional connectivity, and access to global business centres.",
    },
    {
        "key": "ownership_clarity",
        "label": "Ownership clarity",
        "weight": 0.12,
        "sources": ["ownership_clarity"],
        "evidence": "Foreign-buyer pathway, title transparency, transaction practicality, and legal friction.",
    },
    {
        "key": "regulatory_safety",
        "label": "Regulatory safety",
        "weight": 0.08,
        "sources": ["str_regulatory_safety"],
        "evidence": "Short-term-rental and local operating rules that can affect income durability.",
    },
    {
        "key": "rental_profit",
        "label": "Rental profit",
        "weight": 0.13,
        "sources": ["rental_profit_potential"],
        "evidence": "Net-yield potential after operating friction, seasonality, and realistic asset selection.",
    },
    {
        "key": "capital_upside",
        "label": "Capital upside",
        "weight": 0.09,
        "sources": ["capital_upside"],
        "evidence": "Long-term appreciation drivers, scarcity, infrastructure, and demand migration.",
    },
    {
        "key": "retirement_fit",
        "label": "Retirement fit",
        "weight": 0.11,
        "sources": ["retirement_suitability", "standard_of_living"],
        "evidence": "Healthcare, convenience, safety, comfort, and the ability to live there for months.",
    },
    {
        "key": "exit_liquidity",
        "label": "Exit liquidity",
        "weight": 0.09,
        "sources": ["exit_liquidity"],
        "evidence": "Depth and quality of the resale buyer pool when the thesis changes.",
    },
    {
        "key": "foreigner_fit",
        "label": "Foreigner fit",
        "weight": 0.07,
        "sources": ["chinese_foreigner_friendliness"],
        "evidence": "Ease for global and Chinese-speaking buyers across language, services, and local acceptance.",
    },
    {
        "key": "value_entry",
        "label": "Value entry",
        "weight": 0.11,
        "sources": ["affordability"],
        "evidence": "Price discipline, USD/m2 reasonableness, and margin of safety at acquisition.",
    },
]


def money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.0f}"


def number(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{value:,.0f}"


def percentish(value: str | None) -> float:
    if not value:
        return 0
    values = [float(part) for part in re.findall(r"\d+(?:\.\d+)?", value)]
    return max(values) if values else 0


def score(dest: dict, key: str) -> float:
    return float(dest.get("scores", {}).get(key, {}).get("score", 0) or 0)


def dimension_score(dest: dict, sources: list[str]) -> float:
    values = [score(dest, key) for key in sources if score(dest, key) > 0]
    return sum(values) / len(values) if values else 0


def consolidate_destination(dest: dict) -> dict:
    dimensions = []
    for item in DIMENSIONS:
        value = dimension_score(dest, item["sources"])
        dimensions.append(
            {
                "key": item["key"],
                "label": item["label"],
                "score": round(value, 2),
                "weight": item["weight"],
                "sources": item["sources"],
                "evidence": item["evidence"],
            }
        )
    consolidated = sum(item["score"] * item["weight"] for item in dimensions)
    enriched = dict(dest)
    enriched["decision_dimensions"] = dimensions
    enriched["decision_score"] = round(consolidated, 2)
    return enriched


def score_width(value: float) -> str:
    return f"{max(0, min(value, 5)) * 20:.0f}%"


def confidence_tone(value: str | None) -> str:
    text = (value or "").lower()
    if "high" in text:
        return "high"
    if "low" in text:
        return "low"
    return "medium"


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build_listing_card(item: dict) -> str:
    return f"""
      <article class="listing">
        <div>
          <p class="listing__type">{escape(item.get("property_type") or "Listing")}</p>
          <h5>{escape(item.get("listing_name") or "Representative listing")}</h5>
          <p>{escape(item.get("note") or "")}</p>
        </div>
        <dl class="listing__facts">
          <div><dt>USD price</dt><dd>{money(item.get("usd_price"))}</dd></div>
          <div><dt>USD/m2</dt><dd>{money(item.get("usd_per_m2"))}</dd></div>
          <div><dt>Size</dt><dd>{number(item.get("size_m2"))} m2</dd></div>
          <div><dt>Local</dt><dd>{escape(item.get("local_currency") or "")} {number(item.get("local_price"))}</dd></div>
        </dl>
        <a class="source-link" href="{escape(item.get("source_url") or "#")}" target="_blank" rel="noreferrer">
          {escape(item.get("source_name") or "Source")} · {escape(item.get("confidence") or "n/a")} confidence
        </a>
      </article>
    """


def build_score_rows(dest: dict) -> str:
    rows = []
    for item in dest.get("decision_dimensions", []):
        key = item["key"]
        value = float(item.get("score", 0) or 0)
        weight = float(item.get("weight", 0) or 0)
        label = item.get("label", key.replace("_", " ").title())
        evidence = item.get("evidence") or "Consolidated decision dimension."
        rows.append(
            f"""
            <li class="score-row" data-score-key="{escape(key)}" data-score-value="{value}" data-score-weight="{weight}">
              <div><span>{escape(label)}</span><strong>{value:.1f}</strong></div>
              <i style="--value: {score_width(value)}"></i>
              <small>Base weight {weight * 100:.0f}%</small>
              <p>{escape(evidence)}</p>
            </li>
            """
        )
    return "\n".join(rows)


def build_evidence_rows(dest: dict) -> str:
    rental = dest.get("rental", {})
    rows = [
        ("USD/m2 benchmark", money(dest.get("usd_per_m2")), dest.get("price_basis") or "Listing-sample benchmark; verify against current local comparables.", dest.get("price_confidence") or "Confidence n/a"),
        ("Net yield", dest.get("net_yield_estimate") or "n/a", rental.get("net_yield") or rental.get("gross_yield") or "Yield estimate needs live underwriting by unit type.", rental.get("confidence") or "Research estimate"),
        ("STR revenue", rental.get("revenue") or "n/a", rental.get("adr_occupancy") or "Occupancy and ADR vary by asset quality, local permit status, and seasonality.", rental.get("confidence") or "Research estimate"),
        ("Ownership clarity", f"{score(dest, 'ownership_clarity'):.1f}/5", dest.get("ownership_notes") or "Confirm title structure, foreign-buyer rules, taxes, and transfer process with local counsel.", "Legal pathway"),
        ("Retirement fit", f"{score(dest, 'retirement_suitability'):.1f}/5", "Composite read across healthcare, access, daily convenience, food, safety, and year-round lifestyle resilience.", "Lifestyle score"),
        ("Exit liquidity", f"{score(dest, 'exit_liquidity'):.1f}/5", "Panel score reflects expected resale depth, buyer pool quality, and market transparency.", "Liquidity score"),
    ]
    return "\n".join(
        f"""
        <article class="evidence-item">
          <div><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>
          <p>{escape(text)}</p>
          <em data-tone="{confidence_tone(tone)}">{escape(tone)}</em>
        </article>
        """
        for label, value, text, tone in rows
    )


def build_weight_controls(destinations: list[dict]) -> str:
    controls = []
    for item in DIMENSIONS:
        key = item["key"]
        weight = float(item.get("weight", 0) or 0)
        label = item["label"]
        controls.append(
            f"""
            <label class="weight-control">
              <span>{escape(label)}</span>
              <input type="range" min="0" max="20" step="1" value="{weight * 100:.0f}" data-weight-key="{escape(key)}">
              <strong>{weight * 100:.0f}%</strong>
            </label>
            """
        )
    return "\n".join(controls)


def build_destination_card(dest: dict, listings: list[dict], top_retirement_ids: set[str]) -> str:
    dest_listings = "\n".join(build_listing_card(item) for item in listings)
    pros = "".join(f"<li>{escape(item)}</li>" for item in dest.get("pros", []))
    cons = "".join(f"<li>{escape(item)}</li>" for item in dest.get("cons", []))
    ownership_score = score(dest, "ownership_clarity")
    retirement_score = score(dest, "retirement_suitability")
    yield_score = percentish(dest.get("net_yield_estimate"))
    price_confidence = dest.get("price_confidence") or "Confidence n/a"
    rental_confidence = dest.get("rental", {}).get("confidence") or "Research estimate"
    open_attr = "open" if dest["rank"] <= 2 else ""
    return f"""
      <details
        class="destination-card"
        data-id="{escape(dest["id"])}"
        data-name="{escape(dest["name"].lower())}"
        data-country="{escape((dest.get("country") or "").lower())}"
        data-category="{escape(dest.get("category") or "")}"
        data-score="{dest.get("decision_score", dest.get("overall_score", 0))}"
        data-price="{dest.get("usd_per_m2", 0)}"
        data-yield="{yield_score}"
        data-ownership="{ownership_score}"
        data-retirement="{retirement_score}"
        data-shortlist="{"yes" if dest["rank"] <= 8 else "no"}"
        data-top-retirement="{"yes" if dest["id"] in top_retirement_ids else "no"}"
        {open_attr}
      >
        <summary>
          <div class="rank-mark"><span>#{dest["rank"]}</span></div>
          <div class="summary-copy">
            <p>{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")}</p>
            <h3>{escape(dest["name"])}</h3>
            <span>{escape(dest.get("panel_verdict") or "")}</span>
          </div>
          <div class="score-dial" aria-label="Decision score {dest.get("decision_score", dest.get("overall_score", 0)):.2f} out of 5">
            <strong data-custom-score>{dest.get("decision_score", dest.get("overall_score", 0)):.2f}</strong>
            <small>/ 5</small>
          </div>
          <label class="summary-compare">
            <input type="checkbox" class="compare-toggle" value="{escape(dest["id"])}">
            Compare
          </label>
        </summary>

        <div class="decision-row">
          <button type="button" class="memo-add" data-memo-id="{escape(dest["id"])}">Add to memo shortlist</button>
        </div>

        <section class="metric-strip" aria-label="Key metrics">
          <div>
            <span>Entry benchmark</span>
            <strong>{money(dest.get("usd_per_m2"))}/m2</strong>
            <em data-tone="{confidence_tone(price_confidence)}">{escape(price_confidence)}</em>
          </div>
          <div>
            <span>Net yield</span>
            <strong>{escape(dest.get("net_yield_estimate") or "n/a")}</strong>
            <em data-tone="{confidence_tone(rental_confidence)}">{escape(rental_confidence)}</em>
          </div>
          <div>
            <span>Ownership clarity</span>
            <strong>{ownership_score:.1f}/5</strong>
            <em>Foreign-buyer pathway</em>
          </div>
          <div>
            <span>Retirement fit</span>
            <strong>{retirement_score:.1f}/5</strong>
            <em>Long-term lifestyle</em>
          </div>
        </section>

        <section class="brief-grid">
          <article>
            <h4>Committee Read</h4>
            <p>{escape(dest.get("panel_summary") or "")}</p>
          </article>
          <article>
            <h4>Investment Edge</h4>
            <p>{escape(dest.get("profit_driver") or "")}</p>
          </article>
          <article>
            <h4>Governance Check</h4>
            <p>{escape(dest.get("ownership_notes") or "")}</p>
            <p class="risk-note">{escape(dest.get("red_flags") or "")}</p>
          </article>
        </section>

        <section class="pros-cons">
          <article><h4>Why It Works</h4><ul>{pros}</ul></article>
          <article><h4>What Can Break</h4><ul>{cons}</ul></article>
        </section>

        <section class="score-board">
          <div class="section-heading">
            <h4>10-Dimension Rating</h4>
            <p>Consolidated from the original granular scorecard into the ten dimensions that drive the buy/no-buy decision.</p>
          </div>
          <ul>{build_score_rows(dest)}</ul>
        </section>

        <section class="evidence-board">
          <div class="section-heading">
            <h4>Metric Evidence</h4>
            <p>Assumption trail for the numbers most likely to drive the buy/no-buy decision.</p>
          </div>
          <div class="evidence-grid">{build_evidence_rows(dest)}</div>
        </section>

        <section class="listings-wrap">
          <div class="section-heading">
            <h4>Representative Live-Market References</h4>
            <p>Three listing samples to anchor price, size, property type, and market texture.</p>
          </div>
          <div class="listings">{dest_listings}</div>
        </section>
      </details>
    """


def build_spotlight(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations[:3]:
        cards.append(
            f"""
            <article class="spotlight-card">
              <span>#{dest["rank"]}</span>
              <h3>{escape(dest["name"])}</h3>
              <p>{escape(dest.get("country") or "")} · {escape(dest.get("category") or "")}</p>
              <dl>
                <div><dt>Decision</dt><dd>{dest.get("decision_score", dest.get("overall_score", 0)):.2f}</dd></div>
                <div><dt>USD/m2</dt><dd>{money(dest.get("usd_per_m2"))}</dd></div>
                <div><dt>Yield</dt><dd>{escape(dest.get("net_yield_estimate") or "n/a")}</dd></div>
              </dl>
            </article>
            """
        )
    return "\n".join(cards)


def build() -> Path:
    destinations = [consolidate_destination(item) for item in load_json("destinations.json")]
    destinations = sorted(destinations, key=lambda item: item["rank"])
    listings = load_json("listings.json")
    fx = load_json("fx_rates.json")
    listings_by_dest: dict[str, list[dict]] = {}
    for listing in listings:
        listings_by_dest.setdefault(listing["destination_id"], []).append(listing)

    top_retirement_ids = {
        item["id"]
        for item in sorted(destinations, key=lambda d: score(d, "retirement_suitability"), reverse=True)[:5]
    }
    cards = "".join(
        build_destination_card(dest, listings_by_dest.get(dest["id"], []), top_retirement_ids)
        for dest in destinations
    )

    avg_score = sum(float(item.get("decision_score", 0) or 0) for item in destinations) / len(destinations)
    min_price = min(float(item.get("usd_per_m2", 0) or 0) for item in destinations)
    countries = len({item.get("country") for item in destinations if item.get("country")})
    categories = sorted({item.get("category") for item in destinations if item.get("category")})
    category_options = "\n".join(
        f'<option value="{escape(category)}">{escape(category)}</option>' for category in categories
    )
    app_data = json.dumps(
        {
            "destinations": destinations,
            "listings": listings,
            "fx": fx,
            "generated": date.today().isoformat(),
        },
        ensure_ascii=False,
    )

    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Global Home Atlas | Compare Global Property Investment Destinations</title>
  <meta name="description" content="Compare global home and property investment destinations with decision scores, ownership clarity, lifestyle fit, yields, and representative market evidence.">
  <link rel="canonical" href="https://globalhomeatlas.com/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Global Home Atlas">
  <meta property="og:title" content="Global Home Atlas">
  <meta property="og:description" content="Compare global home and property investment destinations with decision scores, ownership clarity, lifestyle fit, yields, and representative market evidence.">
  <meta property="og:url" content="https://globalhomeatlas.com/">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"Global Home Atlas","url":"https://globalhomeatlas.com/","description":"Compare global home and property investment destinations with decision scores, ownership clarity, lifestyle fit, yields, and representative market evidence."}</script>
  <style>
    :root {
      color: #15211d;
      background: #f6f3ee;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-synthesis: none;
      text-rendering: optimizeLegibility;
      --ink: #15211d;
      --muted: #66736c;
      --line: rgba(21, 33, 29, .12);
      --paper: #fffdf8;
      --cream: #f6f3ee;
      --deep: #10241f;
      --teal: #176b62;
      --gold: #a77a35;
      --clay: #b85f3f;
      --blue: #536d93;
      --shadow: 0 20px 60px rgba(16, 36, 31, .10);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; min-width: 320px; }
    button, input, select { font: inherit; }
    button { cursor: pointer; }
    a { color: var(--teal); overflow-wrap: anywhere; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    p { line-height: 1.55; }
    .shell { width: min(1220px, calc(100% - 32px)); margin: 0 auto; }
    .hero {
      position: relative;
      isolation: isolate;
      min-height: 88vh;
      display: grid;
      align-items: end;
      padding: 24px 0 28px;
      color: #fffdf8;
      background:
        linear-gradient(135deg, rgba(16, 36, 31, .95), rgba(22, 55, 55, .74) 42%, rgba(167, 122, 53, .34)),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='1000' viewBox='0 0 1600 1000'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1' y1='0' y2='1'%3E%3Cstop stop-color='%230d2527'/%3E%3Cstop offset='.48' stop-color='%232c645f'/%3E%3Cstop offset='1' stop-color='%23c9a86b'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1600' height='1000' fill='url(%23g)'/%3E%3Cpath d='M0 704C190 622 291 603 450 645c168 45 256 137 442 98 169-35 261-159 427-154 108 3 197 59 281 129v282H0Z' fill='%23f6f3ee' fill-opacity='.16'/%3E%3Cpath d='M0 383c126-50 239-53 347-12 152 57 246 35 395-52 142-83 290-143 468-88 154 48 250 148 390 128v641H0Z' fill='%23fffdf8' fill-opacity='.08'/%3E%3Cpath d='M120 170h1360M120 288h1360M120 406h1360M120 524h1360M120 642h1360M120 760h1360M260 90v820M520 90v820M780 90v820M1040 90v820M1300 90v820' stroke='%23fffdf8' stroke-opacity='.10'/%3E%3Ccircle cx='1220' cy='264' r='96' fill='%23fffdf8' fill-opacity='.13'/%3E%3C/svg%3E");
      background-size: cover;
      background-position: center;
    }
    .hero::after {
      content: "";
      position: absolute;
      inset: auto 0 0;
      height: 34%;
      background: linear-gradient(180deg, rgba(246, 243, 238, 0), var(--cream));
      z-index: -1;
    }
    .topbar {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      z-index: 2;
      padding: 18px 0;
    }
    .topbar__inner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 850; letter-spacing: .02em; }
    .brand-mark {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(255, 253, 248, .45);
      border-radius: 50%;
      background: rgba(255, 253, 248, .08);
    }
    .top-links { display: flex; gap: 18px; align-items: center; }
    .top-links a { color: rgba(255, 253, 248, .86); text-decoration: none; font-size: 13px; font-weight: 750; }
    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
      gap: 28px;
      align-items: end;
      padding-top: 92px;
    }
    .eyebrow {
      margin: 0 0 12px;
      color: #d7b980;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      max-width: 930px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(44px, 8vw, 104px);
      line-height: .88;
      letter-spacing: 0;
    }
    .lede {
      max-width: 760px;
      margin: 24px 0 0;
      color: rgba(255, 253, 248, .82);
      font-size: clamp(16px, 2.2vw, 20px);
    }
    .trust-panel {
      padding: 18px;
      border: 1px solid rgba(255, 253, 248, .24);
      border-radius: 8px;
      background: rgba(255, 253, 248, .10);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }
    .trust-panel h2 {
      margin: 0 0 12px;
      font-size: 15px;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    .trust-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .trust-grid div { padding: 12px; border-radius: 6px; background: rgba(255, 253, 248, .11); }
    .trust-grid span { display: block; color: rgba(255, 253, 248, .66); font-size: 11px; font-weight: 850; text-transform: uppercase; }
    .trust-grid strong { display: block; margin-top: 5px; font-size: 22px; }
    .hero-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 26px; }
    .primary-action, .secondary-action {
      min-height: 46px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      border-radius: 6px;
      font-weight: 850;
      text-decoration: none;
    }
    .primary-action { background: #fffdf8; color: var(--deep); }
    .secondary-action { border: 1px solid rgba(255, 253, 248, .34); color: #fffdf8; }
    main { margin-top: -34px; position: relative; z-index: 3; }
    .insight-bar {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--line);
      box-shadow: var(--shadow);
    }
    .insight-bar div { min-width: 0; padding: 18px; background: var(--paper); }
    .insight-bar span, dt {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .06em;
      text-transform: uppercase;
    }
    .insight-bar strong { display: block; margin-top: 7px; font-size: clamp(20px, 3vw, 28px); }
    .workbench {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
      padding: 24px 0 54px;
    }
    .control-panel {
      position: sticky;
      top: 14px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 253, 248, .92);
      box-shadow: 0 12px 40px rgba(16, 36, 31, .08);
      backdrop-filter: blur(18px);
    }
    .control-panel h2 { margin: 0 0 4px; font-size: 19px; }
    .control-panel p { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
    .toolbar { display: grid; gap: 10px; }
    .field label { display: block; margin: 0 0 6px; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .toolbar input, .toolbar select {
      min-height: 46px;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 0 12px;
    }
    .lens-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px; }
    .lens-grid button, .export-row button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 800;
    }
    .lens-grid button[aria-pressed="true"] { background: var(--deep); color: #fffdf8; border-color: var(--deep); }
    .export-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
    .weight-panel {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }
    .weight-panel h3 { margin: 0 0 8px; font-size: 14px; }
    .weight-panel p { margin: 0 0 10px; color: var(--muted); font-size: 12px; }
    .weight-controls { display: grid; gap: 9px; }
    .weight-control {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 96px 38px;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
      font-weight: 780;
    }
    .weight-control input { width: 100%; accent-color: var(--teal); }
    .weight-control strong { color: var(--ink); text-align: right; font-size: 12px; }
    .compare-panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .compare-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .compare-actions button, .decision-row button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 850;
      padding: 0 12px;
    }
    .compare-table-wrap { overflow-x: auto; }
    .compare-table { width: 100%; border-collapse: collapse; min-width: 720px; }
    .compare-table th, .compare-table td {
      padding: 11px 12px;
      border-top: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }
    .compare-table th { color: var(--muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }
    .compare-empty { padding: 18px; color: var(--muted); border-top: 1px solid var(--line); }
    .decision-row {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      align-items: center;
      padding: 0 18px 16px;
    }
    .method-card {
      margin-top: 16px;
      padding: 14px;
      border-radius: 8px;
      background: #eef3f0;
    }
    .method-card h3 { margin: 0 0 8px; font-size: 14px; }
    .method-card ul { margin: 0; padding-left: 18px; color: var(--muted); font-size: 13px; line-height: 1.45; }
    .mobile-jump {
      display: none;
      gap: 8px;
      overflow-x: auto;
      padding: 12px 16px;
      margin: 0 -16px;
      scrollbar-width: none;
    }
    .mobile-jump a {
      flex: 0 0 auto;
      padding: 9px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
      font-weight: 800;
    }
    .content-stack { display: grid; gap: 18px; min-width: 0; }
    .section-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }
    .section-header h2 { margin: 0; font-size: clamp(22px, 4vw, 34px); font-family: Georgia, "Times New Roman", serif; }
    .section-header p { margin: 6px 0 0; color: var(--muted); max-width: 680px; }
    #resultCount { white-space: nowrap; color: var(--muted); font-size: 13px; font-weight: 850; }
    .spotlight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--line); }
    .spotlight-card { min-width: 0; padding: 18px; background: #fffdf8; }
    .spotlight-card span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: var(--deep);
      color: #fffdf8;
      font-weight: 900;
    }
    .spotlight-card h3 { margin: 14px 0 4px; font-size: 19px; }
    .spotlight-card p { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
    .spotlight-card dl { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 0; }
    .spotlight-card dd { margin: 4px 0 0; font-weight: 850; }
    .cards { display: grid; gap: 12px; }
    .destination-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .destination-card[open] { box-shadow: var(--shadow); }
    summary {
      min-height: 116px;
      display: grid;
      grid-template-columns: 56px minmax(0, 1fr) 84px 96px;
      gap: 14px;
      align-items: center;
      padding: 18px;
      cursor: pointer;
      list-style: none;
    }
    summary::-webkit-details-marker { display: none; }
    .rank-mark {
      width: 48px;
      height: 48px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: #eef3f0;
      color: var(--deep);
      font-weight: 900;
    }
    .summary-copy p { margin: 0 0 6px; color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .summary-copy h3 { margin: 0 0 6px; font-size: clamp(20px, 3.4vw, 26px); line-height: 1.05; }
    .summary-copy span {
      display: -webkit-box;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.4;
      overflow: hidden;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    .score-dial {
      width: 76px;
      height: 76px;
      display: grid;
      place-items: center;
      align-content: center;
      border: 1px solid rgba(23, 107, 98, .2);
      border-radius: 50%;
      background: radial-gradient(circle at 50% 50%, #fff 52%, #dbe9e5 53%);
      text-align: center;
    }
    .score-dial strong { display: block; color: var(--teal); font-size: 21px; line-height: 1; }
    .score-dial small { color: var(--muted); font-weight: 800; }
    .summary-compare {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
    }
    .summary-compare input { width: 17px; height: 17px; accent-color: var(--teal); }
    .metric-strip {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: var(--line);
      border-top: 1px solid var(--line);
    }
    .metric-strip div { min-width: 0; padding: 16px 18px; background: #fbfaf6; }
    .metric-strip strong { display: block; margin: 6px 0; font-size: 19px; }
    .metric-strip em {
      display: inline-flex;
      max-width: 100%;
      padding: 4px 7px;
      border-radius: 999px;
      background: #edf3f1;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .metric-strip em[data-tone="high"] { background: #e7f2dc; color: #47652f; }
    .metric-strip em[data-tone="low"] { background: #f8e8df; color: #8a3f28; }
    .brief-grid, .pros-cons {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1px;
      background: var(--line);
      border-top: 1px solid var(--line);
    }
    .brief-grid article, .pros-cons article, .score-board, .listings-wrap { padding: 18px; background: var(--paper); }
    .brief-grid h4, .pros-cons h4, .section-heading h4 { margin: 0 0 8px; font-size: 14px; letter-spacing: .04em; text-transform: uppercase; }
    .brief-grid p, .pros-cons li, .section-heading p, .listing p { color: var(--muted); font-size: 14px; }
    .risk-note { color: #8a3f28 !important; }
    .pros-cons { grid-template-columns: repeat(2, 1fr); }
    .pros-cons ul { margin: 0; padding-left: 18px; }
    .score-board, .listings-wrap { border-top: 1px solid var(--line); }
    .section-heading { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 14px; }
    .section-heading p { margin: 0; max-width: 560px; }
    .score-board ul {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .score-row {
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .score-row div { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
    .score-row span { color: var(--muted); font-size: 13px; font-weight: 760; }
    .score-row strong { font-size: 15px; }
    .score-row i {
      display: block;
      height: 6px;
      margin-top: 8px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--teal) var(--value), #e6e1d8 var(--value));
    }
    .score-row small { display: block; margin-top: 6px; color: var(--muted); font-size: 11px; font-weight: 760; }
    .score-row p { margin: 7px 0 0; color: var(--muted); font-size: 12px; line-height: 1.4; }
    .evidence-board { padding: 18px; border-top: 1px solid var(--line); background: var(--paper); }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .evidence-item { padding: 13px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .evidence-item div { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .evidence-item span { color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .evidence-item strong { font-size: 15px; }
    .evidence-item p { margin: 8px 0; color: var(--muted); font-size: 13px; }
    .evidence-item em {
      display: inline-flex;
      padding: 4px 7px;
      border-radius: 999px;
      background: #edf3f1;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
      font-weight: 800;
    }
    .listings { display: grid; gap: 10px; }
    .listing {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(220px, .74fr);
      gap: 14px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }
    .listing__type { margin: 0 0 5px; color: var(--gold) !important; font-size: 11px !important; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .listing h5 { margin: 0 0 5px; font-size: 16px; }
    .listing p { margin: 0; }
    .listing__facts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 9px; margin: 0; }
    .listing dd { margin: 3px 0 0; font-weight: 900; }
    .source-link { grid-column: 1 / -1; font-size: 13px; font-weight: 850; }
    .research-note {
      padding: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    .hidden { display: none; }
    @media (max-width: 980px) {
      .hero { min-height: auto; padding-bottom: 66px; }
      .hero-grid, .workbench { grid-template-columns: 1fr; }
      .control-panel { position: static; }
      .mobile-jump { display: flex; }
      .spotlight-grid { grid-template-columns: 1fr; }
      .metric-strip, .brief-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 680px) {
      .shell { width: min(100% - 28px, 1220px); }
      .top-links { display: none; }
      .hero { min-height: auto; align-items: end; padding-bottom: 36px; }
      .hero-grid { gap: 16px; padding-top: 78px; }
      h1 { font-size: clamp(38px, 11vw, 48px); }
      .lede { margin-top: 18px; font-size: 16px; }
      .hero-actions { margin-top: 18px; }
      .trust-panel { padding: 14px; }
      .trust-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .trust-grid div { padding: 10px; }
      .trust-grid strong { font-size: 20px; }
      .insight-bar, .metric-strip, .brief-grid, .pros-cons, .score-board ul, .evidence-grid, .listing, .listing__facts { grid-template-columns: 1fr; }
      .insight-bar { margin: 0 -2px; }
      main { margin-top: -24px; }
      .workbench { padding-top: 14px; }
      .section-header, .section-heading { display: block; }
      #resultCount { display: block; margin-top: 8px; }
      summary { grid-template-columns: 44px minmax(0, 1fr); gap: 12px; min-height: 0; padding: 15px; align-items: start; }
      .rank-mark { width: 40px; height: 40px; }
      .score-dial { grid-column: 2; width: auto; height: auto; display: flex; justify-content: flex-start; gap: 4px; border: 0; border-radius: 0; background: transparent; text-align: left; }
      .summary-compare { grid-column: 2; justify-content: flex-start; width: max-content; padding: 0 10px; }
      .summary-copy span { -webkit-line-clamp: 3; }
      .brief-grid article, .pros-cons article, .score-board, .evidence-board, .listings-wrap, .section-header, .research-note { padding: 15px; }
      .metric-strip div { padding: 14px 15px; }
      .lens-grid, .export-row { grid-template-columns: 1fr 1fr; }
    }
  </style>
</head>
<body>
  <header class="hero" id="top">
    <nav class="topbar" aria-label="Primary">
      <div class="shell topbar__inner">
        <div class="brand"><span class="brand-mark">G</span><span>Global Home Atlas</span></div>
        <div class="top-links">
          <a href="#shortlist">Shortlist</a>
          <a href="#research">Research Method</a>
          <a href="#destinations">Destinations</a>
        </div>
      </div>
    </nav>
    <div class="shell hero-grid">
      <div>
        <p class="eyebrow">Global home and investment intelligence</p>
        <h1>Global Home Atlas</h1>
        <p class="lede">A research-grade atlas for affluent global buyers comparing lifestyle, ownership clarity, yield realism, exit liquidity, and long-term retirement optionality across 25 property destinations.</p>
        <div class="hero-actions">
          <a class="primary-action" href="#destinations">Explore destinations</a>
          <a class="secondary-action" href="#research">Review methodology</a>
        </div>
      </div>
      <aside class="trust-panel" aria-label="Credibility snapshot">
        <h2>Built for decisions, not browsing</h2>
        <div class="trust-grid">
          <div><span>Destinations</span><strong>__DEST_COUNT__</strong></div>
          <div><span>Countries</span><strong>__COUNTRY_COUNT__</strong></div>
          <div><span>Listing samples</span><strong>__LISTING_COUNT__</strong></div>
          <div><span>FX date</span><strong>__FX_AS_OF__</strong></div>
        </div>
      </aside>
    </div>
  </header>

  <main>
    <div class="shell">
      <section class="insight-bar" aria-label="Dataset summary">
        <div><span>Top score</span><strong>__TOP_SCORE__</strong></div>
        <div><span>Average score</span><strong>__AVG_SCORE__</strong></div>
        <div><span>Lowest USD/m2</span><strong>__LOW_PRICE__</strong></div>
        <div><span>Generated</span><strong>__GENERATED__</strong></div>
      </section>

      <div class="workbench">
        <aside class="control-panel" id="research">
          <h2>Research Console</h2>
          <p>Filter by thesis, then open each destination for the committee read, risk checks, scores, and listing evidence.</p>
          <form class="toolbar" id="toolbar">
            <div class="field">
              <label for="search">Search</label>
              <input id="search" type="search" placeholder="Destination or country" aria-label="Search destination or country">
            </div>
            <div class="field">
              <label for="category">Terrain</label>
              <select id="category" aria-label="Filter by category">
                <option value="all">All terrain types</option>
                __CATEGORY_OPTIONS__
              </select>
            </div>
            <div class="field">
              <label for="sort">Sort by</label>
              <select id="sort" aria-label="Sort destinations">
                <option value="rank">Panel rank</option>
                <option value="score">Overall score</option>
                <option value="price">Lowest USD/m2</option>
                <option value="yield">Yield potential</option>
                <option value="ownership">Ownership clarity</option>
                <option value="retirement">Retirement suitability</option>
              </select>
            </div>
            <div class="field">
              <label>Investor lens</label>
              <div class="lens-grid" role="group" aria-label="Quick view">
                <button type="button" data-quick="all" aria-pressed="true">All</button>
                <button type="button" data-quick="shortlist">Shortlist</button>
                <button type="button" data-quick="ownership">Clean title</button>
                <button type="button" data-quick="retirement">Retire well</button>
              </div>
            </div>
          </form>
          <div class="export-row">
            <button type="button" id="export">JSON</button>
            <button type="button" id="exportCsv">CSV</button>
          </div>
          <div class="weight-panel">
            <h3>10-Dimension Weights</h3>
            <p>Adjust the investment lens and the decision score recalculates across every destination.</p>
            <div class="weight-controls">
              __WEIGHT_CONTROLS__
            </div>
          </div>
          <div class="mobile-jump" aria-label="Mobile navigation">
            <a href="#shortlist">Shortlist</a>
            <a href="#compare">Compare</a>
            <a href="#destinations">All destinations</a>
            <a href="#top">Top</a>
          </div>
          <div class="method-card">
            <h3>Decision Standard</h3>
            <ul>
              <li>Foreign ownership and exit friction are scored before romance.</li>
              <li>Yield is treated as underwriting context, not a promise.</li>
              <li>Listings are evidence anchors, not availability guarantees.</li>
            </ul>
          </div>
        </aside>

        <div class="content-stack">
          <section class="section-card" id="shortlist">
            <div class="section-header">
              <div>
                <h2>Priority Shortlist</h2>
                <p>The top three markets surface immediately so credibility is established before the user has to dig.</p>
              </div>
            </div>
            <div class="spotlight-grid">
              __SPOTLIGHT__
            </div>
          </section>

          <section class="compare-panel" id="compare">
            <div class="section-header">
              <div>
                <h2>Compare 2-4 Destinations</h2>
                <p>Select destinations from the dossiers to compare score, ownership, value, yield, retirement fit, and investment thesis.</p>
              </div>
              <div class="compare-actions">
                <button type="button" id="clearCompare">Clear</button>
                <button type="button" id="exportMemo">Export memo</button>
              </div>
            </div>
            <div id="compareOutput" class="compare-empty">Select at least two destinations to build a comparison table.</div>
          </section>

          <section class="section-card" id="destinations">
            <div class="section-header">
              <div>
                <h2>Destination Dossiers</h2>
                <p>Each dossier combines investment thesis, lifestyle durability, legal clarity, and representative live-market listings.</p>
              </div>
              <span id="resultCount">__DEST_COUNT__ shown</span>
            </div>
            <div class="cards" id="cards">
              __CARDS__
            </div>
            <p class="research-note">FX as of __FX_AS_OF__. Listing data is research-grade and changes quickly; verify live availability, tax treatment, permits, title structure, and local counsel advice before any investment decision.</p>
          </section>
        </div>
      </div>
    </div>
  </main>

  <script type="application/json" id="app-data">__APP_DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById("app-data").textContent);
    const cards = Array.from(document.querySelectorAll(".destination-card"));
    const cardsRoot = document.getElementById("cards");
    const search = document.getElementById("search");
    const category = document.getElementById("category");
    const sort = document.getElementById("sort");
    const resultCount = document.getElementById("resultCount");
    const lensButtons = Array.from(document.querySelectorAll("[data-quick]"));
    const weightInputs = Array.from(document.querySelectorAll("[data-weight-key]"));
    const compareOutput = document.getElementById("compareOutput");
    const compareSelected = new Set();
    const memoShortlist = new Set();
    let quickView = "all";

    const destinationsById = new Map(data.destinations.map((destination) => [destination.id, destination]));
    data.destinations.forEach((destination) => {
      destination.custom_score = destination.decision_score;
    });

    function cardRank(card) {
      return Number(card.querySelector(".rank-mark span").textContent.replace("#", ""));
    }

    function activeWeights() {
      const raw = Object.fromEntries(weightInputs.map((input) => [input.dataset.weightKey, Number(input.value)]));
      const total = Object.values(raw).reduce((sum, value) => sum + value, 0);
      if (!total) {
        return Object.fromEntries(data.destinations[0].decision_dimensions.map((item) => [item.key, item.weight]));
      }
      return Object.fromEntries(Object.entries(raw).map(([key, value]) => [key, value / total]));
    }

    function recalculateScores() {
      const weights = activeWeights();
      weightInputs.forEach((input) => {
        input.closest(".weight-control").querySelector("strong").textContent = input.value + "%";
      });
      data.destinations.forEach((destination) => {
        const score = destination.decision_dimensions.reduce((sum, item) => sum + item.score * (weights[item.key] || 0), 0);
        destination.custom_score = Number(score.toFixed(2));
        const card = document.querySelector(`.destination-card[data-id="${destination.id}"]`);
        if (card) {
          card.dataset.score = destination.custom_score;
          card.querySelector("[data-custom-score]").textContent = destination.custom_score.toFixed(2);
        }
      });
      renderCompare();
      applyFilters();
    }

    function applyFilters() {
      const query = search.value.trim().toLowerCase();
      const selectedCategory = category.value;
      let shown = 0;

      cards.forEach((card) => {
        const matchesQuery = !query || card.dataset.name.includes(query) || card.dataset.country.includes(query);
        const matchesCategory = selectedCategory === "all" || card.dataset.category === selectedCategory;
        const matchesQuick =
          quickView === "all" ||
          (quickView === "shortlist" && card.dataset.shortlist === "yes") ||
          (quickView === "ownership" && Number(card.dataset.ownership) >= 4) ||
          (quickView === "retirement" && card.dataset.topRetirement === "yes");
        const visible = matchesQuery && matchesCategory && matchesQuick;
        card.classList.toggle("hidden", !visible);
        if (visible) shown += 1;
      });

      const sorted = [...cards].sort((a, b) => {
        if (sort.value === "score") return Number(b.dataset.score) - Number(a.dataset.score);
        if (sort.value === "price") return Number(a.dataset.price) - Number(b.dataset.price);
        if (sort.value === "yield") return Number(b.dataset.yield) - Number(a.dataset.yield);
        if (sort.value === "ownership") return Number(b.dataset.ownership) - Number(a.dataset.ownership);
        if (sort.value === "retirement") return Number(b.dataset.retirement) - Number(a.dataset.retirement);
        return cardRank(a) - cardRank(b);
      });
      sorted.forEach((card) => cardsRoot.appendChild(card));
      resultCount.textContent = shown + (shown === 1 ? " destination shown" : " destinations shown");
    }

    function destinationMetric(destination, key) {
      return destination.decision_dimensions.find((item) => item.key === key)?.score || 0;
    }

    function selectedCompareDestinations() {
      return [...compareSelected].map((id) => destinationsById.get(id)).filter(Boolean);
    }

    function renderCompare() {
      const selected = selectedCompareDestinations();
      if (selected.length < 2) {
        compareOutput.className = "compare-empty";
        compareOutput.textContent = selected.length === 1
          ? "Select one more destination to build a comparison table."
          : "Select at least two destinations to build a comparison table.";
        return;
      }
      compareOutput.className = "compare-table-wrap";
      const rows = [
        ["Decision score", ...selected.map((d) => d.custom_score.toFixed(2))],
        ["USD/m2", ...selected.map((d) => "$" + Number(d.usd_per_m2 || 0).toLocaleString())],
        ["Net yield", ...selected.map((d) => d.net_yield_estimate || "n/a")],
        ["Ownership", ...selected.map((d) => destinationMetric(d, "ownership_clarity").toFixed(1) + "/5")],
        ["Rental profit", ...selected.map((d) => destinationMetric(d, "rental_profit").toFixed(1) + "/5")],
        ["Retirement fit", ...selected.map((d) => destinationMetric(d, "retirement_fit").toFixed(1) + "/5")],
        ["Exit liquidity", ...selected.map((d) => destinationMetric(d, "exit_liquidity").toFixed(1) + "/5")],
        ["Panel thesis", ...selected.map((d) => d.profit_driver || d.panel_verdict || "n/a")]
      ];
      compareOutput.innerHTML = `
        <table class="compare-table">
          <thead><tr><th>Metric</th>${selected.map((d) => `<th>${d.name}<br><small>${d.country || ""}</small></th>`).join("")}</tr></thead>
          <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${String(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      `;
    }

    function setCompare(id, checked) {
      if (checked && compareSelected.size >= 4 && !compareSelected.has(id)) {
        document.querySelector(`.compare-toggle[value="${id}"]`).checked = false;
        return;
      }
      if (checked) compareSelected.add(id);
      else compareSelected.delete(id);
      renderCompare();
    }

    search.addEventListener("input", applyFilters);
    category.addEventListener("change", applyFilters);
    sort.addEventListener("change", applyFilters);
    weightInputs.forEach((input) => input.addEventListener("input", recalculateScores));
    lensButtons.forEach((button) => {
      button.addEventListener("click", () => {
        quickView = button.dataset.quick;
        lensButtons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
        applyFilters();
      });
    });
    document.querySelectorAll(".compare-toggle").forEach((checkbox) => {
      checkbox.addEventListener("change", () => setCompare(checkbox.value, checkbox.checked));
    });
    document.querySelectorAll(".summary-compare").forEach((label) => {
      label.addEventListener("click", (event) => event.stopPropagation());
    });
    document.querySelectorAll(".memo-add").forEach((button) => {
      button.addEventListener("click", () => {
        const id = button.dataset.memoId;
        if (memoShortlist.has(id)) {
          memoShortlist.delete(id);
          button.textContent = "Add to memo shortlist";
        } else {
          memoShortlist.add(id);
          button.textContent = "Remove from memo";
        }
      });
    });
    document.getElementById("clearCompare").addEventListener("click", () => {
      compareSelected.clear();
      document.querySelectorAll(".compare-toggle").forEach((checkbox) => {
        checkbox.checked = false;
      });
      renderCompare();
    });

    function downloadFile(filename, type, content) {
      const blob = new Blob([content], { type });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }

    document.getElementById("export").addEventListener("click", () => {
      downloadFile("destination-property-dashboard-data.json", "application/json", JSON.stringify(data, null, 2));
    });

    document.getElementById("exportCsv").addEventListener("click", () => {
      const rows = [
        ["rank", "destination", "country", "category", "decision_score", "custom_score", "usd_per_m2", "net_yield", "ownership_score", "retirement_score"],
        ...data.destinations.map((d) => [
          d.rank,
          d.name,
          d.country || "",
          d.category || "",
          d.decision_score,
          d.custom_score,
          d.usd_per_m2,
          d.net_yield_estimate || "",
          destinationMetric(d, "ownership_clarity"),
          destinationMetric(d, "retirement_fit")
        ])
      ];
      const csv = rows.map((row) => row.map((cell) => '"' + String(cell).replaceAll('"', '""') + '"').join(",")).join("\\n");
      downloadFile("destination-property-summary.csv", "text/csv", csv);
    });

    function memoDestinations() {
      if (compareSelected.size >= 2) return selectedCompareDestinations();
      if (memoShortlist.size) return [...memoShortlist].map((id) => destinationsById.get(id)).filter(Boolean);
      return [...data.destinations].sort((a, b) => b.custom_score - a.custom_score).slice(0, 4);
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      })[char]);
    }

    function buildMemoHtml() {
      const selected = memoDestinations();
      const generated = new Date().toISOString().slice(0, 10);
      const rows = selected.map((d) => `
        <section>
          <h2>${escapeHtml(d.name)} <span>${escapeHtml(d.country || "")}</span></h2>
          <dl>
            <div><dt>Decision score</dt><dd>${d.custom_score.toFixed(2)} / 5</dd></div>
            <div><dt>USD/m2</dt><dd>$${Number(d.usd_per_m2 || 0).toLocaleString()}</dd></div>
            <div><dt>Net yield</dt><dd>${escapeHtml(d.net_yield_estimate || "n/a")}</dd></div>
            <div><dt>Ownership</dt><dd>${destinationMetric(d, "ownership_clarity").toFixed(1)} / 5</dd></div>
          </dl>
          <h3>Investment thesis</h3>
          <p>${escapeHtml(d.profit_driver || d.panel_summary || "")}</p>
          <h3>Risk check</h3>
          <p>${escapeHtml(d.red_flags || "Verify title, tax, permit, and local market liquidity before committing capital.")}</p>
          <h3>10-dimension rating</h3>
          <table>
            <tbody>${d.decision_dimensions.map((item) => `<tr><th>${escapeHtml(item.label)}</th><td>${Number(item.score).toFixed(1)}</td><td>${escapeHtml(item.evidence)}</td></tr>`).join("")}</tbody>
          </table>
        </section>
      `).join("");
      return `<!doctype html>
        <html><head><meta charset="utf-8"><title>Investor Shortlist Memo</title>
        <style>
          body{font-family:Inter,Arial,sans-serif;margin:40px;color:#15211d;background:#fffdf8;line-height:1.5}
          h1{font-family:Georgia,serif;font-size:42px;line-height:1;margin:0 0 8px} h2{margin-top:32px;border-top:1px solid #ddd4c7;padding-top:24px}
          h2 span{color:#66736c;font-size:16px;font-weight:500} h3{margin-bottom:6px;font-size:13px;text-transform:uppercase;letter-spacing:.06em}
          dl{display:grid;grid-template-columns:repeat(4,1fr);gap:10px} dl div{border:1px solid #ddd4c7;padding:10px;border-radius:6px}
          dt{color:#66736c;font-size:11px;text-transform:uppercase;font-weight:800} dd{margin:4px 0 0;font-weight:800}
          table{width:100%;border-collapse:collapse;margin-top:8px} th,td{text-align:left;border-top:1px solid #ddd4c7;padding:8px;vertical-align:top;font-size:13px}
          @media(max-width:720px){body{margin:20px}dl{grid-template-columns:1fr}}
        </style></head><body>
        <h1>Investor Shortlist Memo</h1>
        <p>Generated ${generated}. Scores use the current 10-dimension weighting model from Global Home Atlas.</p>
        ${rows}
        </body></html>`;
    }

    document.getElementById("exportMemo").addEventListener("click", () => {
      downloadFile("investor-shortlist-memo.html", "text/html", buildMemoHtml());
    });

    recalculateScores();
  </script>
</body>
</html>
"""
    replacements = {
        "__DEST_COUNT__": str(len(destinations)),
        "__COUNTRY_COUNT__": str(countries),
        "__LISTING_COUNT__": str(len(listings)),
        "__FX_AS_OF__": escape(fx.get("as_of", "n/a")),
        "__TOP_SCORE__": f"{destinations[0]['decision_score']:.2f}",
        "__AVG_SCORE__": f"{avg_score:.2f}",
        "__LOW_PRICE__": money(min_price),
        "__GENERATED__": date.today().isoformat(),
        "__CATEGORY_OPTIONS__": category_options,
        "__WEIGHT_CONTROLS__": build_weight_controls(destinations),
        "__SPOTLIGHT__": build_spotlight(destinations),
        "__CARDS__": cards,
        "__APP_DATA__": app_data,
    }
    for key, value in replacements.items():
        html = html.replace(key, value)

    ARTIFACTS.mkdir(exist_ok=True)
    out = ARTIFACTS / "unified_destination_dashboard.html"
    index = ARTIFACTS / "index.html"
    out.write_text(html, encoding="utf-8")
    index.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build())
