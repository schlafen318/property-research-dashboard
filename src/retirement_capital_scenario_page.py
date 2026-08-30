from __future__ import annotations

from html import escape


SCENARIO_LABELS = {
    500_000: "$500,000",
    750_000: "$750,000",
    1_000_000: "$1 million",
    1_500_000: "$1.5 million",
    2_000_000: "$2 million",
}


def _money(value: float) -> str:
    sign = "−" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def _destination_row(item: dict, destination: dict) -> str:
    gap = float(item["surplusGap"])
    gap_text = f"{_money(gap)} remaining" if gap >= 0 else f"{_money(abs(gap))} shortfall"
    country_link = (
        f'<a href="{escape(destination["countryGuideHref"])}" data-track="retirement_capital_scenario_guide_click" '
        f'data-destination-id="{escape(item["destinationId"])}" data-link-type="country">Country guide</a>'
        if destination.get("countryGuideHref")
        else ""
    )
    return f"""
      <article class="scenario-row">
        <div><h3>{escape(item['name'])}</h3><p>{escape(item['country'])} · {escape(item['tier'].replace('_', ' ').title())}</p></div>
        <dl><div><dt>Required capital</dt><dd>{_money(float(item['retirementTarget']))}</dd></div><div><dt>Position</dt><dd>{gap_text}</dd></div></dl>
        <nav><a href="/destinations/{escape(item['destinationId'])}/" data-track="retirement_capital_scenario_guide_click" data-destination-id="{escape(item['destinationId'])}" data-link-type="destination">Destination guide</a>{country_link}</nav>
      </article>
    """.strip()


def build_retirement_capital_scenario_html(
    *,
    slug: str,
    capital_usd: int,
    result: dict,
    destinations_by_id: dict[str, dict],
    head: str,
    navigation: str,
    footer: str,
    analytics: str,
    design_css: str,
    scenario_links: list[tuple[str, str]],
) -> str:
    label = SCENARIO_LABELS[capital_usd]
    recommendations = result.get("recommendations", [])
    within = [item for item in recommendations if item.get("tier") == "within_reach"]
    alternatives = [item for item in recommendations if item.get("tier") != "within_reach"][:5]
    strongest = recommendations[0] if recommendations else None
    if within and strongest:
        answer = (
            f"{len(within)} destinations are Within reach. "
            f"{escape(strongest['name'])} is the strongest match for this planning estimate."
        )
    elif strongest:
        answer = (
            f"No destinations are Within reach. {escape(strongest['name'])} is the closest match, "
            f"with a {_money(abs(float(strongest['surplusGap'])))} shortfall."
        )
    else:
        answer = "No destinations have enough cost data for this planning estimate."
    within_rows = "".join(
        _destination_row(item, destinations_by_id.get(item["destinationId"], {}))
        for item in within
    )
    alternative_rows = "".join(
        _destination_row(item, destinations_by_id.get(item["destinationId"], {}))
        for item in alternatives
    )
    destination_sections = ""
    if within_rows:
        destination_sections += f"<section><h2>Destinations Within reach</h2>{within_rows}</section>"
    if alternative_rows:
        destination_sections += f"<section><h2>Closest alternatives</h2>{alternative_rows}</section>"
    links = "".join(
        f'<a href="/{escape(link_slug)}/">{escape(link_label)}</a>'
        for link_slug, link_label in scenario_links
    )
    return f"""<!doctype html>
<html lang="en"><head>{head}<style>{design_css}
.retirement-scenario-page .scenario-shell{{width:min(960px,calc(100% - 48px));margin-inline:auto}}.retirement-scenario-page .scenario-hero{{padding:56px 0 46px;border-bottom:1px solid var(--gha-rule)}}.retirement-scenario-page .scenario-eyebrow{{margin:0 0 14px;color:var(--gha-accent);font-size:12px;letter-spacing:.08em;text-transform:uppercase}}.retirement-scenario-page h1,.retirement-scenario-page h2,.retirement-scenario-page h3{{font-family:var(--gha-display-serif);font-weight:500}}.retirement-scenario-page h1{{max-width:820px;margin:0;font-size:clamp(46px,6vw,72px);line-height:1}}.retirement-scenario-page .scenario-answer{{max-width:760px;margin:28px 0 0;font-family:var(--gha-display-serif);font-size:23px}}.retirement-scenario-page main{{padding:0 0 72px}}.retirement-scenario-page section{{padding:40px 0;border-bottom:1px solid var(--gha-rule)}}.retirement-scenario-page h2{{margin:0 0 18px;font-size:clamp(32px,4vw,46px)}}.retirement-scenario-page .scenario-assumptions{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin:0}}.retirement-scenario-page dt{{color:var(--gha-muted);font-size:12px}}.retirement-scenario-page dd{{margin:4px 0 0}}.retirement-scenario-page .scenario-row{{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(260px,1fr) auto;gap:24px;align-items:start;padding:20px 0;border-top:1px solid var(--gha-rule)}}.retirement-scenario-page .scenario-row h3{{margin:0;font-size:27px}}.retirement-scenario-page .scenario-row p{{margin:3px 0;color:var(--gha-muted)}}.retirement-scenario-page .scenario-row dl{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:0}}.retirement-scenario-page .scenario-row nav,.retirement-scenario-page .scenario-links{{display:grid;gap:7px}}.retirement-scenario-page .scenario-note{{color:var(--gha-muted);font-size:14px}}.retirement-scenario-page .scenario-action{{display:inline-flex;min-height:46px;align-items:center;padding:0 18px;background:var(--gha-ink);color:var(--gha-paper);text-decoration:none;text-transform:uppercase;font-size:12px;letter-spacing:.05em}}.retirement-scenario-page details{{padding:14px 0;border-top:1px solid var(--gha-rule)}}.retirement-scenario-page summary{{cursor:pointer;font-weight:400}}@media(max-width:760px){{.retirement-scenario-page .scenario-shell{{width:min(100% - 32px,960px)}}.retirement-scenario-page .scenario-assumptions,.retirement-scenario-page .scenario-row{{grid-template-columns:1fr}}.retirement-scenario-page .scenario-row dl{{grid-template-columns:1fr 1fr}}}}
</style></head><body class="gha-mode-utility retirement-scenario-page" data-scenario-slug="{escape(slug)}">{navigation}
<header class="scenario-hero"><div class="scenario-shell"><p class="scenario-eyebrow">Retirement capital guide</p><h1>Where can you retire abroad with {label}?</h1><p class="scenario-answer">{answer}</p></div></header>
<main><div class="scenario-shell"><section><p class="scenario-eyebrow">Planning estimate</p><h2>What this comparison assumes</h2><dl class="scenario-assumptions"><div><dt>Capital at retirement</dt><dd>{label}</dd></div><div><dt>Household</dt><dd>Couple</dd></div><div><dt>Retirement period</dt><dd>30 years</dd></div><div><dt>Housing</dt><dd>Rent</dd></div><div><dt>Portfolio return</dt><dd>5% annual portfolio return</dd></div><div><dt>Reserve</dt><dd>12 months of expenses</dd></div></dl></section>
{destination_sections}
<section><h2>Test your retirement plan</h2><p>Use your own timeline, capital, income and housing plan.</p><a class="scenario-action" href="/retirement-destination-finder/" data-track="retirement_capital_scenario_calculator_start" data-link-type="calculator">Open the retirement finder</a></section>
<section><h2>Compare other capital levels</h2><nav class="scenario-links">{links}</nav></section>
<section><h2>Planning notes</h2><p class="scenario-note">This is a planning estimate, not a guarantee of affordability, visa eligibility, tax treatment, healthcare access or property-purchase eligibility. Review current rules and personal circumstances before acting. <a href="/methodology/">Read the methodology</a>.</p></section>
<section><h2>Frequently asked questions</h2><details><summary>Is {label} enough to retire abroad?</summary><p>It is Within reach where the capital covers the required retirement capital under these assumptions. Your personal result may differ.</p></details><details><summary>Does this include buying a home?</summary><p>No. This comparison assumes renting. Use the finder to test a purchase at retirement.</p></details><details><summary>Are tax and visa costs included?</summary><p>No. Confirm immigration and tax requirements separately.</p></details></section></div></main>{footer}{analytics}</body></html>"""
