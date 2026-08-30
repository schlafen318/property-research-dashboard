from __future__ import annotations

import json
from html import escape


def _money(value: object) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return "Not available"
    return f"${value:,.0f}"


def _score(value: object) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return "Needs verification"
    return f"{value:.2f} out of 5"


def _status_label(value: object) -> str:
    return {
        "eligible": "Eligible",
        "conditional": "Conditional",
        "needs_verification": "Needs verification",
        "not_eligible": "Not currently eligible",
    }.get(str(value), "Needs verification")


def _work_permission_label(value: object) -> str:
    return {
        "passive_only": "Passive income only",
        "remote_permitted": "Remote work permitted",
        "local_permitted": "Local work permitted",
        "unclear": "Work permission needs professional review",
    }.get(str(value), "Work permission needs professional review")


def _default_result_rows(default_results: list[dict]) -> str:
    rows = []
    for result in default_results:
        destination_id = escape(str(result.get("destination_id", "")))
        name = escape(str(result.get("name", destination_id)))
        status = _status_label(result.get("status"))
        status_reason = escape(str(result.get("status_reason", "")))
        score_value = result.get("score")
        score_text = (
            f"FIRE Abroad score: {score_value:.2f} out of 5"
            if isinstance(score_value, (int, float)) and not isinstance(score_value, bool)
            else "Ranking: Unranked until evidence is verified"
        )
        components = result.get("components", {})
        components = components if isinstance(components, dict) else {}
        budget = result.get("resilience_budget", {})
        budget = budget if isinstance(budget, dict) else {}
        warnings = result.get("warnings", [])
        warning = next((item for item in warnings if isinstance(item, str) and item), "Verify current legal, tax, healthcare, and cost evidence before acting.")
        strongest_activity = result.get("strongest_activity_reason") or "Review the Active Life evidence for everyday movement and year-round continuity."
        rows.append(
            f"""
          <tr data-fire-result="{destination_id}">
            <th scope="row" data-label="Destination"><a href="/destinations/{destination_id}/" data-fire-track="destination_guide_click" data-fire-destination-id="{destination_id}">{name}</a><span>{escape(status)}</span><small>{status_reason}</small></th>
            <td data-label="FIRE Abroad score"><strong>{escape(score_text)}</strong><span>Active Life: {_score(components.get("active_life"))}</span><small>{escape(str(strongest_activity))}</small></td>
            <td data-label="Resilience budget"><strong>{_money(budget.get("annual_total_usd"))} per year</strong><span>Currency and inflation buffer: {_money(budget.get("currency_inflation_buffer"))}</span><small>One-time relocation estimate: {_money(budget.get("one_time_relocation_usd"))}</small></td>
            <td data-label="Planning checks"><span>Healthcare Bridge: {_score(components.get("healthcare_bridge"))}</span><span>Stay Flexibility: {_score(components.get("stay_flexibility"))}</span><span>{escape(_work_permission_label(result.get("work_permission")))}</span><span>Tax Compatibility: {_score(components.get("tax_compatibility"))}</span><small>{escape(str(warning))}</small></td>
            <td data-label="Evidence and next steps"><span>{escape(str(result.get("confidence", "low")).replace("_", " ").title())} confidence</span><span>Evidence reviewed {escape(str(result.get("last_reviewed") or "not recorded"))}</span><a href="/retirement-abroad-calculator/?destination={destination_id}&amp;household=single&amp;housing=rent" data-fire-track="calculator_handoff" data-fire-destination-id="{destination_id}">Build your plan</a><a href="/destinations/{destination_id}/" data-fire-track="destination_guide_click" data-fire-destination-id="{destination_id}">Read destination guide</a></td>
          </tr>""".rstrip()
        )
    return "\n".join(rows)


def _evidence_list(payload: dict) -> str:
    fire_payload = payload.get("fire_payload", {})
    retirement_costs = payload.get("retirement_costs", {})
    items: list[str] = []
    for country_name, country in fire_payload.get("countries", {}).items():
        for source in country.get("sources", []):
            items.append(
                '<li><a href="{url}" rel="nofollow noopener">{publisher}: {metric}</a> '
                '(source {source_date}; accessed {accessed_date}; {country})</li>'.format(
                    url=escape(str(source.get("url", ""))),
                    publisher=escape(str(source.get("publisher", "Source"))),
                    metric=escape(str(source.get("metric_supported", "supporting evidence"))),
                    source_date=escape(str(source.get("source_date", "not recorded"))),
                    accessed_date=escape(str(source.get("accessed_date", "not recorded"))),
                    country=escape(str(country_name)),
                )
            )
    for cost in retirement_costs.get("destinations", []):
        destination_id = escape(str(cost.get("destination_id", "destination")))
        for source in cost.get("sources", []):
            items.append(
                '<li><a href="{url}" rel="nofollow noopener">{name}</a> '
                '(source {source_date}; cost evidence for {destination})</li>'.format(
                    url=escape(str(source.get("url", ""))),
                    name=escape(str(source.get("name", "Cost source"))),
                    source_date=escape(str(source.get("source_date", "not recorded"))),
                    destination=destination_id,
                )
            )
    return "\n".join(items)


def build_fire_abroad_html(
    *,
    head: str,
    navigation: str,
    default_results: list[dict],
    payload_json: str,
    engine_js: str,
    ui_js: str,
    design_css: str,
    analytics: str,
    footer: str,
) -> str:
    """Render a coherent default FIRE Abroad page before browser scripts run."""

    ranked_count = sum(
        1 for result in default_results if isinstance(result.get("score"), (int, float))
    )
    unranked_count = len(default_results) - ranked_count
    summary = f"{ranked_count} ranked destinations"
    if unranked_count:
        summary += f"; {unranked_count} need verification."
    else:
        summary += "."
    result_rows = _default_result_rows(default_results)
    payload = json.loads(payload_json)
    evidence_rows = _evidence_list(payload)
    reviewed_on = escape(
        str(payload.get("fire_payload", {}).get("reviewed_on", "not recorded"))
    )
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
  <style id="fire-abroad-page-style">
    .fire-abroad-page .fire-content {{ max-width: 1120px; padding: 52px 0 76px; }}
    .fire-abroad-page .fire-breadcrumb {{ margin: 0 0 18px; color: var(--gha-muted); font-size: 13px; }}
    .fire-abroad-page .fire-breadcrumb a {{ color: inherit; }}
    .fire-abroad-page .fire-profile {{ margin: 0 0 58px; padding: 28px 0 32px; border-top: 3px solid var(--gha-ink); border-bottom: 1px solid var(--gha-rule); }}
    .fire-abroad-page .fire-profile h2, .fire-abroad-page .fire-results-section h2, .fire-abroad-page .fire-methodology h2, .fire-abroad-page .fire-sources h2 {{ margin: 0 0 12px; }}
    .fire-abroad-page .fire-profile > p, .fire-abroad-page .fire-methodology > p, .fire-abroad-page .fire-sources > p {{ max-width: 780px; color: var(--gha-muted); }}
    .fire-abroad-page .fire-fields {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; margin-top: 24px; }}
    .fire-abroad-page .fire-field {{ min-width: 0; }}
    .fire-abroad-page .fire-field label {{ display: block; min-height: 38px; margin-bottom: 6px; font-size: 13px; }}
    .fire-abroad-page .fire-field input, .fire-abroad-page .fire-field select {{ width: 100%; min-height: 46px; padding: 9px 10px; border: 1px solid var(--gha-rule); }}
    .fire-abroad-page .fire-profile button {{ min-height: 46px; margin-top: 22px; padding: 0 18px; border: 1px solid var(--gha-ink); background: var(--gha-ink); color: var(--gha-paper); cursor: pointer; }}
    .fire-abroad-page .fire-profile button:hover {{ background: var(--gha-accent); }}
    .fire-abroad-page #fire-results-summary {{ margin: 0 0 20px; color: var(--gha-muted); }}
    .fire-abroad-page .fire-table-wrap {{ overflow-x: auto; }}
    .fire-abroad-page .fire-results-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .fire-abroad-page .fire-results-table th, .fire-abroad-page .fire-results-table td {{ padding: 16px 14px; border-top: 1px solid var(--gha-rule); text-align: left; vertical-align: top; line-height: 1.5; }}
    .fire-abroad-page .fire-results-table thead th {{ color: var(--gha-muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }}
    .fire-abroad-page .fire-results-table tbody th {{ width: 18%; font-size: 15px; }}
    .fire-abroad-page .fire-results-table span, .fire-abroad-page .fire-results-table small, .fire-abroad-page .fire-results-table a {{ display: block; margin-top: 7px; }}
    .fire-abroad-page .fire-results-table small {{ color: var(--gha-muted); font-size: 12px; }}
    .fire-abroad-page #fire-results > article {{ padding: 24px 0; border-top: 1px solid var(--gha-rule); }}
    .fire-abroad-page #fire-results > article h2 {{ margin: 0 0 10px; font-size: 28px; }}
    .fire-abroad-page #fire-results > article p {{ max-width: 780px; margin: 7px 0; }}
    .fire-abroad-page #fire-results > article a {{ display: inline-flex; min-height: 44px; align-items: center; margin-right: 20px; }}
    .fire-abroad-page .fire-methodology, .fire-abroad-page .fire-sources {{ margin-top: 64px; padding-top: 42px; border-top: 3px solid var(--gha-ink); }}
    .fire-abroad-page .fire-weights {{ width: min(100%, 760px); border-collapse: collapse; margin-top: 24px; }}
    .fire-abroad-page .fire-weights th, .fire-abroad-page .fire-weights td {{ padding: 11px 8px 11px 0; border-top: 1px solid var(--gha-rule); text-align: left; }}
    .fire-abroad-page .fire-evidence {{ margin-top: 24px; border-top: 1px solid var(--gha-rule); }}
    .fire-abroad-page .fire-evidence summary {{ min-height: 48px; display: flex; align-items: center; font-weight: 500; cursor: pointer; }}
    .fire-abroad-page .fire-evidence li {{ max-width: 920px; margin: 10px 0; overflow-wrap: anywhere; }}
    .fire-abroad-page noscript p {{ padding: 14px 0; border-top: 1px solid var(--gha-rule); border-bottom: 1px solid var(--gha-rule); }}
    @media (max-width: 900px) {{ .fire-abroad-page .fire-fields {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 760px) {{
      .fire-abroad-page .fire-results-table, .fire-abroad-page .fire-results-table tbody, .fire-abroad-page .fire-results-table tr, .fire-abroad-page .fire-results-table th, .fire-abroad-page .fire-results-table td {{ display: block; width: 100%; }}
      .fire-abroad-page .fire-results-table thead {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; }}
      .fire-abroad-page .fire-results-table tr {{ padding: 22px 0; border-top: 2px solid var(--gha-ink); }}
      .fire-abroad-page .fire-results-table th, .fire-abroad-page .fire-results-table td {{ padding: 7px 0; border: 0; }}
      .fire-abroad-page .fire-results-table td::before {{ content: attr(data-label); display: block; margin-bottom: 3px; color: var(--gha-muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }}
    }}
    @media (max-width: 560px) {{ .fire-abroad-page .fire-fields {{ grid-template-columns: 1fr; }} .fire-abroad-page .fire-field label {{ min-height: 0; }} .fire-abroad-page .fire-profile button {{ width: 100%; }} }}
  </style>
  <style id="gha-top-level-design">{design_css}</style>
</head>
<body class="gha-mode-utility gha-top-level fire-abroad-page" data-design-system="gha-v1" data-default-stay-mode="part_year">
{navigation}
<header class="page-hero"><div class="page-shell">
  <nav class="fire-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a> / FIRE Abroad</nav>
  <p class="page-eyebrow">Active financial independence overseas</p>
  <h1>FIRE Abroad</h1>
  <p class="page-lede"><strong>FIRE means Financial Independence, Retire Early.</strong> FIRE Abroad compares places where financial independence can support an active life overseas, whether you want a seasonal stay, a part-year base, or a full relocation.</p>
  <p class="page-lede">Residence is mode-dependent. Property ownership is optional, and a high score never guarantees legal stay, tax, healthcare, or work eligibility.</p>
</div></header>
<main><div class="gha-shell fire-content">
  <form id="fire-abroad-form" class="fire-profile">
    <h2>Set your planning profile</h2>
    <p>The defaults compare one person renting a part-year base at age 50. Optional context stays in this browser and is not added to calculator links.</p>
    <div class="fire-fields">
      <div class="fire-field"><label for="fire-stay-mode">Intended stay</label><select id="fire-stay-mode"><option value="seasonal">Seasonal</option><option value="part_year" selected>Part-year base</option><option value="full_relocation">Full relocation</option></select></div>
      <div class="fire-field"><label for="fire-age">Current age</label><input id="fire-age" type="number" min="18" max="100" value="50"></div>
      <div class="fire-field"><label for="fire-household">Household</label><select id="fire-household"><option value="single" selected>Single</option><option value="couple">Couple</option></select></div>
      <div class="fire-field"><label for="fire-housing">Housing</label><select id="fire-housing"><option value="rent" selected>Rent</option><option value="own">Already own</option><option value="buy_now">Buy now</option><option value="buy_retirement">Buy at retirement</option></select></div>
      <div class="fire-field"><label for="fire-mobility-rights">Mobility rights context (optional)</label><select id="fire-mobility-rights"><option value="prefer_not_to_say" selected>Prefer not to say</option><option value="local_free_movement">Local or free-movement rights</option><option value="general_nonlocal">General nonlocal passport</option></select></div>
      <div class="fire-field"><label for="fire-home-tax-context">Home tax context (optional)</label><select id="fire-home-tax-context"><option value="prefer_not_to_say" selected>Prefer not to say</option><option value="us_person">U.S. person</option><option value="other">Other</option></select></div>
      <div class="fire-field"><label for="fire-annual-days">Approximate days per year (optional)</label><input id="fire-annual-days" type="number" min="1" max="366" placeholder="Not set"></div>
      <div class="fire-field"><label for="fire-income-type">Income type (optional)</label><select id="fire-income-type"><option value="prefer_not_to_say" selected>Prefer not to say</option><option value="portfolio">Portfolio</option><option value="pension">Pension</option><option value="property">Property</option><option value="business_consulting">Business or consulting</option><option value="mixed">Mixed</option></select></div>
      <div class="fire-field"><label for="fire-activity-priority">Activity priority (optional)</label><select id="fire-activity-priority"><option value="balanced" selected>Balanced Active Life</option><option value="walking">Walking</option><option value="cycling">Cycling</option><option value="hiking">Hiking</option><option value="water">Water activities</option><option value="winter_sports">Winter sports</option><option value="fitness_social">Fitness and social activity</option></select></div>
    </div>
    <button type="submit">Update ranking</button>
  </form>
  <section class="fire-results-section" aria-labelledby="fire-results-heading">
    <h2 id="fire-results-heading">Default FIRE Abroad ranking</h2>
    <p id="fire-results-summary" aria-live="polite">{escape(summary)}</p>
    <noscript><p>JavaScript is optional. The default part-year ranking remains available below; use the linked destination research and calculator to continue planning.</p></noscript>
    <div id="fire-results" aria-live="polite"><div class="fire-table-wrap"><table class="fire-results-table"><caption>Age 50, single household, renting a part-year base</caption><thead><tr><th>Destination and eligibility</th><th>Score and Active Life</th><th>Resilience budget</th><th>Planning checks</th><th>Evidence and next steps</th></tr></thead><tbody>
{result_rows}
    </tbody></table></div></div>
  </section>
  <section class="fire-methodology" id="methodology">
    <h2>How FIRE Abroad scores destinations</h2>
    <p>The score combines eight evidence-backed dimensions. <strong>Immigration status and tax residence are separate tests</strong>: a lawful stay does not settle tax residence, and local-source income can matter even when you are not resident.</p>
    <table class="fire-weights"><caption>FIRE Abroad score methodology</caption><tbody>
      <tr><th scope="row">25% Active Life</th><td>Everyday movement, active pursuits, year-round continuity, and activity ecosystem.</td></tr>
      <tr><th scope="row">20% sustainable annual cost</th><td>Comfortable recurring costs plus a resilience allowance.</td></tr>
      <tr><th scope="row">15% Healthcare Bridge</th><td>Practical access from arrival through longer-term life.</td></tr>
      <tr><th scope="row">10% Stay Flexibility</th><td>Credible route for the selected duration, including work-permission limits.</td></tr>
      <tr><th scope="row">10% Tax Compatibility</th><td>Clarity and administrative complexity, not a personal tax calculation.</td></tr>
      <tr><th scope="row">8% Global Access</th><td>Practical international and family connections.</td></tr>
      <tr><th scope="row">7% Community Fit</th><td>Practical social and daily-life fit for a foreign resident or repeat visitor.</td></tr>
      <tr><th scope="row">5% Property and Exit Flexibility</th><td>Renting, optional ownership, liquidity, and the ability to avoid lock-in.</td></tr>
    </tbody></table>
    <p><strong>Resilience budget:</strong> recurring living, housing, private healthcare, travel, visa and administration, contingency, and a currency and inflation buffer. One-time relocation and property capital remain separate. These are screening estimates, not financial, tax, immigration, healthcare, or investment advice.</p>
  </section>
  <section class="fire-sources" id="sources">
    <h2>Evidence and limitations</h2>
    <p>Evidence reviewed {reviewed_on}. Costs and rules change; check the source dates, current eligibility, and personal circumstances before acting.</p>
    <details class="fire-evidence"><summary>Source evidence and review dates</summary><ul>
{evidence_rows}
    </ul></details>
  </section>
</div></main>
{footer}
<script id="fire-abroad-data" type="application/json">{payload_json}</script>
<script>{engine_js}</script>
<script>{ui_js}</script>
<script>(function(){{function init(){{GHAFireAbroadUI.initFireAbroad(window);}}if(document.readyState==="loading"){{document.addEventListener("DOMContentLoaded",init,{{once:true}});}}else{{init();}}}})();</script>
{analytics}
</body>
</html>"""
