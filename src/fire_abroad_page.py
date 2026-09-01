from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any


def _money(value: Any) -> str:
    if value is None:
        return "—"
    return f"${float(value):,.0f}"


def _label(value: str) -> str:
    labels = {
        "likely_nonresident": "Likely nonresident",
        "residence_depends_on_days_and_ties": "Depends on days and ties",
        "likely_resident": "Likely resident",
        "straightforward": "Straightforward",
        "moderate": "Moderate",
        "complex": "Complex",
        "highly_profile_dependent": "Highly profile-dependent",
    }
    return labels.get(value, value.replace("_", " ").title())


def _result_rows(rows: list[dict[str, Any]]) -> str:
    rendered = []
    for row in rows:
        if not row["rankable"]:
            eligibility = row.get("eligibility", {})
            if row["tax"]["status"] == "tax_impact_unavailable":
                reason = "Research pending — tax evidence is incomplete, so this destination is not ranked."
            else:
                reason = "Eligibility check needed — " + eligibility.get("summary", "verify a legal stay route before ranking.")
            rendered.append(
                f"""
                <tr>
                  <th scope="row">{escape(row['name'])}<small>{escape(row['country'])}</small></th>
                  <td colspan="6"><strong>{escape(reason)}</strong></td>
                </tr>
                """
            )
            continue
        tax = row["tax"]
        budget = row["budget"]
        calculator = (
            "/retirement-abroad-calculator/?destination=" + escape(row["destination_id"]) +
            "&amp;household=single&amp;housing=rent"
        )
        rendered.append(
            f"""
            <tr>
              <th scope="row">{escape(row['name'])}<small>{escape(row['country'])}</small></th>
              <td>{row['overall_score']:.2f}/5</td>
              <td><strong>{_label(row['eligibility']['status'])}</strong><small>{escape(row['eligibility']['summary'])}</small></td>
              <td><strong>{_label(tax['residence_outcome'])}</strong><small>{escape(tax['scope_summary'])}</small></td>
              <td><strong>{_label(tax['readiness'])}</strong><small>{escape(tax['confidence'].replace('_', '-'))} confidence</small></td>
              <td><strong>{_money(budget['central_tax_reserve'])}</strong><small>{_money(budget['favorable_tax_reserve'])}–{_money(budget['adverse_tax_reserve'])}</small></td>
              <td><a href="{calculator}">Build your plan</a></td>
            </tr>
            """
        )
    return "".join(rendered)


def _property_lifecycle(countries: dict[str, Any]) -> tuple[str, str]:
    complete = next(
        ((name, country["tax_screen"]) for name, country in countries.items() if country["tax_screen"].get("status") == "complete"),
        None,
    )
    if not complete:
        return "", ""
    country_name, screen = complete
    lifecycle = screen["property_lifecycle"]
    stages = (
        ("Purchase", "purchase"),
        ("Annual ownership", "annual"),
        ("Rental operation", "rental"),
        ("Sale", "sale"),
        ("Inheritance or gift", "succession"),
    )
    return country_name, "".join(
        f"<dt>{escape(label)}</dt><dd>{escape(lifecycle[key]['summary'])}</dd>"
        for label, key in stages
    )


def _sources(sources: list[dict[str, Any]]) -> str:
    return "".join(
        f'<li><a href="{escape(source["url"])}" rel="noopener noreferrer">{escape(source["publisher"])}</a> — {escape(source["metric_supported"])}</li>'
        for source in sources
    )


def build_fire_abroad_html(
    *,
    head: str,
    navigation: str,
    footer: str,
    rows: list[dict[str, Any]],
    countries: dict[str, Any],
    sources: list[dict[str, Any]],
    reviewed_on: str,
    payload_json: str,
    engine_js: str,
    ui_js: str,
    design_css: str,
    analytics: str,
) -> str:
    reviewed = datetime.strptime(reviewed_on, "%Y-%m-%d").strftime("%-d %B %Y")
    lifecycle_country, lifecycle_html = _property_lifecycle(countries)
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
  <style>
    .fire-shell{{width:min(1160px,calc(100% - 40px));margin:0 auto}}
    .fire-hero{{padding:64px 0 34px;background:#f5f1e9}}
    .fire-hero p{{max-width:760px}}
    .fire-form{{padding:28px 0;border-top:1px solid rgba(36,49,45,.15);border-bottom:1px solid rgba(36,49,45,.15)}}
    .fire-fields{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
    .fire-fields label{{display:grid;gap:7px;font-weight:600}}
    .fire-fields select{{width:100%;min-height:44px;padding:8px;border:1px solid #9aa59f;background:#fff}}
    .fire-results,.fire-method{{padding:38px 0}}
    .fire-table-wrap{{overflow-x:auto}}
    .fire-table{{width:100%;border-collapse:collapse;min-width:880px}}
    .fire-table th,.fire-table td{{padding:14px 12px;border-bottom:1px solid rgba(36,49,45,.14);text-align:left;vertical-align:top}}
    .fire-table th small,.fire-table td small{{display:block;margin-top:5px;color:#68776f;font-weight:400;max-width:240px}}
    .fire-table a{{font-weight:650}}
    .fire-tax-note{{max-width:820px;color:#4d5b55}}
    .fire-lifecycle{{display:grid;grid-template-columns:180px 1fr;gap:10px 22px;max-width:900px}}
    .fire-lifecycle dt{{font-weight:700}}
    .fire-lifecycle dd{{margin:0 0 8px}}
    .fire-sources li{{margin-bottom:8px}}
    @media(max-width:760px){{.fire-fields{{grid-template-columns:1fr}}.fire-lifecycle{{grid-template-columns:1fr}}}}
  </style>
  <style id="gha-top-level-design">{design_css}</style>
</head>
<body class="gha-mode-utility gha-top-level fire-abroad-page" data-design-system="gha-v1">
{navigation}
<main>
  <header class="fire-hero"><div class="fire-shell">
    <nav aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / FIRE Abroad</nav>
    <p class="eyebrow">Financial independence overseas</p>
    <h1>FIRE Abroad</h1>
    <p>Compare an active life abroad without ignoring tax. Start with a few plain-language choices, see a planning range, and open the detail only when you need it.</p>
  </div></header>
  <section class="fire-form" aria-labelledby="fire-screen-heading"><div class="fire-shell">
    <h2 id="fire-screen-heading">Your quick screen</h2>
    <div class="fire-fields">
      <label for="fire-stay">How will you use the destination?<select id="fire-stay"><option value="seasonal">Seasonal stays</option><option value="part_year" selected>Part-year base</option><option value="full_relocation">Full relocation</option></select></label>
      <label for="fire-days">Approximate time there each year<select id="fire-days"><option value="under_90">Under 90 days</option><option value="90_182">90–182 days</option><option value="183_plus">183 days or more</option><option value="unsure" selected>Not sure</option></select></label>
      <label for="fire-income">Main source of spending money<select id="fire-income"><option value="portfolio" selected>Investment portfolio</option><option value="pension">Pension</option><option value="property">Property income</option><option value="work_business">Work or business</option><option value="mixed">Mixed</option></select></label>
      <label for="fire-housing">Housing plan<select id="fire-housing"><option value="rent" selected>Rent</option><option value="own">Already own</option><option value="buy_now">Buy now</option><option value="buy_retirement">Buy later</option></select></label>
      <label data-fire-group="property-use" hidden for="fire-property-use">How would you use the home?<select id="fire-property-use"><option value="personal">Personal use</option><option value="rental">Rental</option><option value="mixed">Mixed use</option></select></label>
      <label for="fire-mobility">Your mobility rights<select id="fire-mobility"><option value="prefer_not_to_say" selected>Not sure</option><option value="local_free_movement">Local or free-movement rights</option><option value="general_nonlocal">Need a visa or residence route</option></select></label>
      <label for="fire-tax-home">Current tax-home system<select id="fire-tax-home"><option value="prefer_not_to_say" selected>Not sure</option><option value="residence_based">Usually based on residence</option><option value="citizenship_based_worldwide">Can continue after moving</option><option value="territorial">Mainly local-source income</option></select></label>
    </div>
  </div></section>
  <section class="fire-results" aria-labelledby="fire-results-heading"><div class="fire-shell">
    <h2 id="fire-results-heading">Tax-aware destination screen</h2>
    <p class="fire-tax-note"><strong>Planning tax reserve</strong> is a broad screening allowance, not a statutory rate or assessment. It is shown separately from <strong>Tax Readiness</strong>, which describes rule clarity and administrative complexity. Likely tax residence is a screen, not an immigration conclusion.</p>
    <div class="fire-table-wrap"><table class="fire-table"><thead><tr><th>Destination</th><th>FIRE score</th><th>Stay eligibility</th><th>Likely tax residence</th><th>Tax Readiness</th><th>Planning tax reserve</th><th>Next step</th></tr></thead><tbody id="fire-results-body" aria-live="polite">{_result_rows(rows)}</tbody></table></div>
    <p><a href="/retirement-abroad-calculator/">Open the retirement calculator</a></p>
  </div></section>
  <section class="fire-method"><div class="fire-shell">
    <h2>{escape(lifecycle_country)} property-tax lifecycle</h2>
    <p>Property tax does not stop at the purchase. Open these stages before relying on a home budget.</p>
    <dl class="fire-lifecycle">{lifecycle_html}</dl>
    <details><summary>Assumptions and primary sources</summary><p>Data checked {escape(reviewed)}. Legal and tax claims use current primary-source evidence; incomplete destinations remain visibly unranked. Planning reserve percentages are product-defined stress-test allowances, not statutory rates or tax estimates.</p><ul class="fire-sources">{_sources(sources)}</ul></details>
  </div></section>
</main>
{footer}
<script type="application/json" id="fire-abroad-data">{payload_json}</script>
<script>{engine_js}</script><script>{ui_js}</script>
<script>GHAFireAbroadUI.initFireAbroad("fire-screen-heading");</script>
{analytics}
</body>
</html>"""
