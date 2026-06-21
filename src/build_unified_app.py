from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"


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


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build() -> Path:
    destinations = sorted(load_json("destinations.json"), key=lambda item: item["rank"])
    listings = load_json("listings.json")
    fx = load_json("fx_rates.json")
    listings_by_dest: dict[str, list[dict]] = {}
    for listing in listings:
        listings_by_dest.setdefault(listing["destination_id"], []).append(listing)

    cards = []
    top_retirement_ids = {
        item["id"]
        for item in sorted(
            destinations,
            key=lambda d: d.get("scores", {})
            .get("retirement_suitability", {})
            .get("score", 0),
            reverse=True,
        )[:5]
    }
    for dest in destinations:
        dest_listings = listings_by_dest.get(dest["id"], [])
        listing_cards = "\n".join(
            f"""
            <article class="listing">
              <div>
                <p class="listing__type">{escape(item.get("property_type") or "Listing")}</p>
                <h4>{escape(item.get("listing_name") or "Representative listing")}</h4>
                <p>{escape(item.get("note") or "")}</p>
              </div>
              <dl>
                <div><dt>USD price</dt><dd>{money(item.get("usd_price"))}</dd></div>
                <div><dt>Local price</dt><dd>{escape(item.get("local_currency") or "")} {number(item.get("local_price"))}</dd></div>
                <div><dt>USD/m²</dt><dd>{money(item.get("usd_per_m2"))}</dd></div>
                <div><dt>Size</dt><dd>{number(item.get("size_m2"))} m²</dd></div>
                <div><dt>Confidence</dt><dd>{escape(item.get("confidence") or "n/a")}</dd></div>
              </dl>
              <a href="{escape(item.get("source_url") or "#")}" target="_blank" rel="noreferrer">{escape(item.get("source_name") or "Source")}</a>
            </article>
            """
            for item in dest_listings
        )
        score_rows = "\n".join(
            f"""
            <li>
              <span>{escape(score.get("label", key.replace("_", " ").title()))}</span>
              <strong>{score.get("score", 0):.1f}</strong>
            </li>
            """
            for key, score in dest.get("scores", {}).items()
        )
        pros = "".join(f"<li>{escape(item)}</li>" for item in dest.get("pros", []))
        cons = "".join(f"<li>{escape(item)}</li>" for item in dest.get("cons", []))
        ownership_score = dest.get("scores", {}).get("ownership_clarity", {}).get("score", 0)
        retirement_score = dest.get("scores", {}).get("retirement_suitability", {}).get("score", 0)
        yield_score = percentish(dest.get("net_yield_estimate"))
        cards.append(
            f"""
            <details
              class="card"
              data-name="{escape(dest["name"].lower())}"
              data-country="{escape((dest.get("country") or "").lower())}"
              data-category="{escape(dest.get("category") or "")}"
              data-score="{dest.get("overall_score", 0)}"
              data-price="{dest.get("usd_per_m2", 0)}"
              data-yield="{yield_score}"
              data-ownership="{ownership_score}"
              data-retirement="{retirement_score}"
              data-shortlist="{"yes" if dest["rank"] <= 8 else "no"}"
              data-top-retirement="{"yes" if dest["id"] in top_retirement_ids else "no"}"
              {"open" if dest["rank"] <= 3 else ""}
            >
              <summary>
                <div class="rank">#{dest["rank"]}</div>
                <div class="summary-main">
                  <p>{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")}</p>
                  <h3>{escape(dest["name"])}</h3>
                  <span>{escape(dest.get("panel_verdict") or "")}</span>
                </div>
                <div class="summary-metrics">
                  <b>{dest.get("overall_score", 0):.2f}</b>
                  <small>overall</small>
                </div>
              </summary>
              <section class="metrics" aria-label="Key metrics">
                <div><span>USD/m²</span><strong>{money(dest.get("usd_per_m2"))}</strong><em class="badge">{escape(dest.get("price_confidence") or "Confidence n/a")}</em></div>
                <div><span>Net yield</span><strong>{escape(dest.get("net_yield_estimate") or "n/a")}</strong><em class="badge">{escape(dest.get("rental", {}).get("confidence") or "Research estimate")}</em></div>
                <div><span>Ownership</span><strong>{ownership_score:.1f}/5</strong><em class="badge">Foreign-buyer clarity</em></div>
              </section>
              <section class="analysis">
                <div>
                  <h4>Panel read</h4>
                  <p>{escape(dest.get("panel_summary") or "")}</p>
                </div>
                <div>
                  <h4>Profit driver</h4>
                  <p>{escape(dest.get("profit_driver") or "")}</p>
                </div>
                <div>
                  <h4>Ownership and red flags</h4>
                  <p>{escape(dest.get("ownership_notes") or "")}</p>
                  <p class="risk">{escape(dest.get("red_flags") or "")}</p>
                </div>
              </section>
              <section class="pros-cons">
                <div><h4>Pros</h4><ul>{pros}</ul></div>
                <div><h4>Cons</h4><ul>{cons}</ul></div>
              </section>
              <section>
                <h4>Score breakdown</h4>
                <ul class="scores">{score_rows}</ul>
              </section>
              <section>
                <h4>Real listings</h4>
                <div class="listings">{listing_cards}</div>
              </section>
            </details>
            """
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

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Holiday & Retirement Property Destination Dashboard</title>
  <style>
    :root {{
      color: #17201b;
      background: #f5f2ec;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-synthesis: none;
      text-rendering: optimizeLegibility;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; }}
    button, input, select {{ font: inherit; }}
    a {{ color: #1d6861; overflow-wrap: anywhere; }}
    .shell {{ width: min(1180px, calc(100% - 28px)); margin: 0 auto; }}
    header {{ padding: 28px 0 14px; }}
    .eyebrow {{ margin: 0 0 8px; color: #7b5a38; font-size: 12px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    h1 {{ margin: 0 0 12px; max-width: 900px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(34px, 8vw, 82px); line-height: .95; letter-spacing: 0; }}
    .lede {{ margin: 0; max-width: 760px; color: #536258; font-size: 16px; line-height: 1.65; }}
    .toolbar {{
      position: sticky; top: 0; z-index: 5; margin: 20px 0; padding: 10px; display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(120px, .7fr) minmax(130px, .8fr) minmax(150px, .9fr) auto auto;
      gap: 8px; background: rgba(245,242,236,.96); border: 1px solid rgba(23,32,27,.1); border-radius: 8px;
      backdrop-filter: blur(16px);
    }}
    .toolbar input, .toolbar select, .toolbar button {{
      min-height: 44px; width: 100%; border: 1px solid rgba(23,32,27,.14); border-radius: 6px; background: #fff; color: #17201b; padding: 0 12px;
    }}
    .toolbar button {{ background: #24443e; color: #fffdf7; font-weight: 800; cursor: pointer; }}
    .meta {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 18px; }}
    .meta div {{ padding: 16px; background: #fff; border: 1px solid rgba(23,32,27,.08); border-radius: 8px; }}
    .meta span, dt {{ display: block; color: #6c766d; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .05em; }}
    .meta strong {{ display: block; margin-top: 6px; font-size: 22px; }}
    .cards {{ display: grid; gap: 12px; padding-bottom: 42px; }}
    .card {{ background: #fff; border: 1px solid rgba(23,32,27,.09); border-radius: 8px; overflow: hidden; }}
    summary {{ min-height: 104px; display: grid; grid-template-columns: 54px minmax(0, 1fr) 74px; gap: 12px; align-items: center; padding: 18px; cursor: pointer; list-style: none; }}
    summary::-webkit-details-marker {{ display: none; }}
    .rank {{ width: 42px; height: 42px; display: grid; place-items: center; border-radius: 50%; background: #edf3f1; color: #24443e; font-weight: 900; }}
    .summary-main p {{ margin: 0 0 5px; color: #7b5a38; font-size: 12px; font-weight: 900; text-transform: uppercase; letter-spacing: .06em; }}
    .summary-main h3 {{ margin: 0 0 5px; font-size: 21px; line-height: 1.1; }}
    .summary-main span {{ color: #536258; font-size: 14px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    .summary-metrics {{ text-align: right; }}
    .summary-metrics b {{ display: block; color: #24443e; font-size: 26px; }}
    .summary-metrics small {{ color: #6c766d; font-weight: 800; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: #eef0eb; }}
    .metrics div {{ padding: 16px 18px; background: #fbfaf6; }}
    .metrics strong {{ display: block; margin: 6px 0; font-size: 20px; }}
    .metrics em {{ color: #69736b; font-size: 12px; font-style: normal; }}
    .badge {{ display: inline-flex; max-width: 100%; padding: 4px 7px; border-radius: 999px; background: #edf3f1; overflow-wrap: anywhere; }}
    section {{ padding: 18px; border-top: 1px solid rgba(23,32,27,.08); }}
    h4 {{ margin: 0 0 8px; font-size: 15px; }}
    p {{ line-height: 1.6; }}
    .analysis, .pros-cons {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .pros-cons {{ grid-template-columns: 1fr 1fr; }}
    .analysis p, .pros-cons li, .listing p {{ color: #536258; font-size: 14px; }}
    .risk {{ color: #8a3f28 !important; }}
    ul {{ margin: 0; padding-left: 18px; }}
    .scores {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; padding: 0; list-style: none; }}
    .scores li {{ display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; background: #f5f2ec; border-radius: 6px; }}
    .listings {{ display: grid; gap: 10px; }}
    .listing {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(190px, .8fr); gap: 14px; padding: 14px; border: 1px solid rgba(23,32,27,.1); border-radius: 8px; background: #fffdf9; }}
    .listing__type {{ margin: 0 0 4px; color: #7b5a38 !important; font-size: 12px !important; font-weight: 900; text-transform: uppercase; letter-spacing: .06em; }}
    .listing h4 {{ margin-bottom: 4px; }}
    .listing dl {{ display: grid; gap: 8px; margin: 0; }}
    .listing dd {{ margin: 2px 0 0; font-weight: 900; }}
    .listing a {{ grid-column: 1 / -1; font-size: 13px; font-weight: 800; }}
    .note {{ margin: 0 0 22px; color: #667168; font-size: 13px; line-height: 1.5; }}
    .hidden {{ display: none; }}
    @media (max-width: 760px) {{
      .toolbar, .meta, .metrics, .analysis, .pros-cons, .scores, .listing {{ grid-template-columns: 1fr; }}
      .toolbar {{ position: static; margin: 14px 0; }}
      summary {{ grid-template-columns: 44px minmax(0, 1fr); align-items: start; }}
      .summary-metrics {{ grid-column: 2; text-align: left; }}
      .summary-main span {{ -webkit-line-clamp: 3; }}
      section, summary {{ padding: 15px; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <p class="eyebrow">Investor-grade destination property research</p>
      <h1>Holiday & retirement property destination dashboard</h1>
      <p class="lede">A mobile-first comparison of 25 global destinations, with scoring, ownership notes, yield caveats, USD/m² benchmarks, and representative real listings embedded per destination.</p>
    </header>
    <form class="toolbar" id="toolbar">
      <input id="search" type="search" placeholder="Search destination or country" aria-label="Search destination or country">
      <select id="category" aria-label="Filter by category">
        <option value="all">All categories</option>
        <option value="Mountain">Mountain</option>
        <option value="Water">Water</option>
        <option value="Mountain + Water">Mountain + Water</option>
      </select>
      <select id="sort" aria-label="Sort destinations">
        <option value="rank">Sort by rank</option>
        <option value="score">Sort by score</option>
        <option value="price">Sort by USD/m²</option>
        <option value="yield">Sort by yield</option>
        <option value="ownership">Sort by ownership clarity</option>
        <option value="retirement">Sort by retirement suitability</option>
      </select>
      <select id="quick" aria-label="Quick view">
        <option value="all">All destinations</option>
        <option value="shortlist">Priority shortlist</option>
        <option value="ownership">Hide low ownership clarity</option>
        <option value="retirement">Top 5 retirement</option>
      </select>
      <button type="button" id="export">Export JSON</button>
      <button type="button" id="exportCsv">CSV</button>
    </form>
    <p class="note">FX as of {escape(fx.get("as_of", "n/a"))}. Listing data is research-grade and changes quickly; verify live availability and legal/tax details before any investment decision.</p>
    <section class="meta" aria-label="Dataset summary">
      <div><span>Destinations</span><strong>{len(destinations)}</strong></div>
      <div><span>Listings</span><strong>{len(listings)}</strong></div>
      <div><span>Top score</span><strong>{destinations[0]["overall_score"]:.2f}</strong></div>
      <div><span>Generated</span><strong>{date.today().isoformat()}</strong></div>
    </section>
    <div class="cards" id="cards">
      {"".join(cards)}
    </div>
  </div>
  <script type="application/json" id="app-data">{app_data}</script>
  <script>
    const data = JSON.parse(document.getElementById("app-data").textContent);
    const cards = Array.from(document.querySelectorAll(".card"));
    const cardsRoot = document.getElementById("cards");
    const search = document.getElementById("search");
    const category = document.getElementById("category");
    const sort = document.getElementById("sort");
    const quick = document.getElementById("quick");

    function applyFilters() {{
      const query = search.value.trim().toLowerCase();
      const selectedCategory = category.value;
      const quickView = quick.value;
      cards.forEach((card) => {{
        const matchesQuery = !query || card.dataset.name.includes(query) || card.dataset.country.includes(query);
        const matchesCategory = selectedCategory === "all" || card.dataset.category === selectedCategory;
        const matchesQuick =
          quickView === "all" ||
          (quickView === "shortlist" && card.dataset.shortlist === "yes") ||
          (quickView === "ownership" && Number(card.dataset.ownership) >= 4) ||
          (quickView === "retirement" && card.dataset.topRetirement === "yes");
        card.classList.toggle("hidden", !(matchesQuery && matchesCategory && matchesQuick));
      }});
      const sorted = [...cards].sort((a, b) => {{
        if (sort.value === "score") return Number(b.dataset.score) - Number(a.dataset.score);
        if (sort.value === "price") return Number(a.dataset.price) - Number(b.dataset.price);
        if (sort.value === "yield") return Number(b.dataset.yield) - Number(a.dataset.yield);
        if (sort.value === "ownership") return Number(b.dataset.ownership) - Number(a.dataset.ownership);
        if (sort.value === "retirement") return Number(b.dataset.retirement) - Number(a.dataset.retirement);
        return Number(a.querySelector(".rank").textContent.replace("#", "")) - Number(b.querySelector(".rank").textContent.replace("#", ""));
      }});
      sorted.forEach((card) => cardsRoot.appendChild(card));
    }}

    search.addEventListener("input", applyFilters);
    category.addEventListener("change", applyFilters);
    sort.addEventListener("change", applyFilters);
    quick.addEventListener("change", applyFilters);
    function downloadFile(filename, type, content) {{
      const blob = new Blob([content], {{ type }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }}
    document.getElementById("export").addEventListener("click", () => {{
      downloadFile("destination-property-dashboard-data.json", "application/json", JSON.stringify(data, null, 2));
    }});
    document.getElementById("exportCsv").addEventListener("click", () => {{
      const rows = [
        ["rank", "destination", "country", "category", "overall_score", "usd_per_m2", "net_yield", "ownership_score", "retirement_score"],
        ...data.destinations.map((d) => [
          d.rank,
          d.name,
          d.country || "",
          d.category || "",
          d.overall_score,
          d.usd_per_m2,
          d.net_yield_estimate || "",
          d.scores?.ownership_clarity?.score || "",
          d.scores?.retirement_suitability?.score || ""
        ])
      ];
      const csv = rows.map((row) => row.map((cell) => '"' + String(cell).replaceAll('"', '""') + '"').join(",")).join("\\n");
      downloadFile("destination-property-summary.csv", "text/csv", csv);
    }});
  </script>
</body>
</html>
"""
    ARTIFACTS.mkdir(exist_ok=True)
    out = ARTIFACTS / "unified_destination_dashboard.html"
    index = ARTIFACTS / "index.html"
    out.write_text(html, encoding="utf-8")
    index.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build())
