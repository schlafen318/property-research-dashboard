from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SITE_ORIGIN = "https://globalhomeatlas.com"
FINDER_ENGINE = ROOT / "src" / "retirement_destination_finder.js"
FINDER_UI = ROOT / "src" / "retirement_destination_finder_ui.js"
DETAILED_TAX_UI = ROOT / "src" / "fire_tax_detailed_ui.js"

KEY_PAGES = [
    ARTIFACTS / "guides" / "index.html",
    ARTIFACTS / "retirement-abroad-calculator" / "index.html",
    ARTIFACTS / "retirement-destination-finder" / "index.html",
    ARTIFACTS / "best-countries-to-buy-property-as-a-foreigner" / "index.html",
    ARTIFACTS / "countries" / "spain-property" / "index.html",
]

REQUIRED_MARKERS = {
    ARTIFACTS / "retirement-abroad-calculator" / "index.html": [
        "Retirement Abroad Calculator",
        "Compare monthly living expenses",
        "Portfolio dividends and interest",
    ],
    ARTIFACTS / "retirement-destination-finder" / "index.html": [
        "Estimate (50% realized gains)",
        "0%–100% realized-gain range",
        "Your financial details stay in this browser",
    ],
    ARTIFACTS / "guides" / "index.html": [
        "Choose the question that matters most to you.",
        "Country and region hubs",
    ],
    ARTIFACTS / "best-countries-to-buy-property-as-a-foreigner" / "index.html": [
        "Decision Path",
        "Turn this guide into a shortlist",
    ],
    ARTIFACTS / "countries" / "spain-property" / "index.html": [
        "Buyer Next Step",
        "Turn Spain research into a shortlist",
    ],
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "link", "script", "img", "source"}:
            return
        lookup = dict(attrs)
        for attr in ("href", "src"):
            value = lookup.get(attr)
            if value:
                self.links.append(value)


def sitemap_count(path: Path) -> int:
    tree = ET.parse(path)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return len(tree.findall(".//sm:url", namespace))


def local_target_exists(link: str) -> bool:
    parsed = urlparse(link)
    if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
        return True
    if parsed.netloc and f"{parsed.scheme}://{parsed.netloc}" != SITE_ORIGIN:
        return True
    path = unquote(parsed.path or "/")
    if not path.startswith("/"):
        return True
    if path.endswith("/"):
        candidate = ARTIFACTS / path.lstrip("/") / "index.html"
    else:
        candidate = ARTIFACTS / path.lstrip("/")
        if candidate.suffix == "":
            candidate = candidate / "index.html"
    return candidate.exists()


def broken_local_links() -> list[str]:
    broken: list[str] = []
    for html_path in ARTIFACTS.rglob("*.html"):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for link in parser.links:
            if not local_target_exists(link):
                broken.append(f"{html_path.relative_to(ROOT)} -> {link}")
    return broken


def finder_handoff_link_errors(links: list[str]) -> list[str]:
    required = {"destination", "household", "housing"}
    errors: list[str] = []
    for link in links:
        parsed = urlparse(link)
        if parsed.path != "/retirement-abroad-calculator/":
            errors.append(f"Finder runtime handoff has unexpected path: {parsed.path}")
            continue
        query = parse_qs(parsed.query, keep_blank_values=True)
        keys = set(query)
        unexpected = sorted(keys - required)
        missing = sorted(required - keys)
        if unexpected:
            errors.append(
                "Finder calculator handoff exposes unexpected query parameters: "
                + ", ".join(unexpected)
            )
        if missing:
            errors.append(
                "Finder calculator handoff is missing required query parameters: "
                + ", ".join(missing)
            )
        destination = query.get("destination", [])
        household = query.get("household", [])
        housing = query.get("housing", [])
        if len(destination) != 1 or not re.fullmatch(r"[a-z0-9-]+", destination[0]):
            errors.append("Finder calculator handoff has an invalid destination")
        if len(household) != 1 or household[0] not in {"single", "couple"}:
            errors.append("Finder calculator handoff has an invalid household")
        if len(housing) != 1 or housing[0] not in {"rent", "own", "buy_now", "buy_retirement"}:
            errors.append("Finder calculator handoff has an invalid housing plan")
    return errors


def finder_runtime_handoff_evidence(html: str) -> dict[str, object]:
    payload_match = re.search(
        r'<script\b[^>]*\bid="retirement-finder-data"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not payload_match:
        raise ValueError("Finder runtime payload is missing")
    payload = json.loads(payload_match.group(1))
    script = r"""
const fs = require("fs");
const finder = require(process.argv[1]);
const ui = require(process.argv[2]);
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
const user = {
  currentAge: 50,
  retirementAge: 65,
  horizonYears: 25,
  household: "single",
  housingPlan: "rent",
  totalLiquidCapital: 500000,
  monthlyPortfolioContribution: 1000,
  contributionInflationLinked: false,
  expectedPortfolioReturn: 0.05,
  returnBasis: "after_fees_and_tax",
  generalInflation: 0.026,
  emergencyReserveMonths: 12,
  incomeStreams: [],
  taxMode: "user_after_tax",
  taxProfile: {
    dependableIncome: 0,
    portfolioWithdrawals: 0,
    realizedGainIntensity: "moderate",
    propertyUse: "none",
    wealthBand: "unknown"
  },
  preferences: {region: "any", climate: "any", healthcare: "normal"},
  purchaseMethod: "cash"
};
const result = finder.recommendDestinations(Object.assign({}, payload, {user}));
const links = ui.calculatorHrefsForResults({recommendations: result.recommendations, user});
process.stdout.write(JSON.stringify({recommendation_count: result.recommendations.length, links}));
"""
    result = subprocess.run(
        ["node", "-e", script, str(FINDER_ENGINE), str(FINDER_UI)],
        input=json.dumps(payload),
        check=True,
        capture_output=True,
        text=True,
    )
    evidence = json.loads(result.stdout)
    return {
        "recommendation_count": int(evidence.get("recommendation_count", 0)),
        "links": list(evidence.get("links", [])),
    }


def finder_handoff_privacy_errors(html: str) -> list[str]:
    try:
        evidence = finder_runtime_handoff_evidence(html)
    except (json.JSONDecodeError, OSError, subprocess.CalledProcessError, ValueError) as error:
        return [f"Finder runtime handoff verification failed: {error}"]
    count = int(evidence["recommendation_count"])
    links = evidence["links"]
    errors: list[str] = []
    if count <= 0:
        errors.append("Finder runtime handoff verification produced no recommendations")
    if len(links) != count:
        errors.append(
            f"Finder runtime handoff verification produced {len(links)} links for {count} recommendations"
        )
    errors.extend(finder_handoff_link_errors(links))
    return errors


def _embedded_json(html: str, element_id: str) -> dict[str, object]:
    match = re.search(
        rf'<script\b[^>]*\bid="{re.escape(element_id)}"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Embedded payload {element_id} is missing")
    payload = json.loads(match.group(1))
    if not isinstance(payload, dict):
        raise ValueError(f"Embedded payload {element_id} is not an object")
    return payload


def detailed_tax_runtime_evidence(html: str) -> dict[str, object]:
    calculator = _embedded_json(html, "retirement-destination-data")
    detailed = _embedded_json(html, "fire-tax-detailed-data")
    destination_ids = [
        item.get("destination_id")
        for item in calculator.get("destinations", [])
        if isinstance(item, dict) and isinstance(item.get("destination_id"), str)
    ]
    script = r"""
let privacyCalls=0;
class Element {
  constructor(id,value="") { this.id=id; this.name=""; this.type=""; this.value=String(value); this.hidden=false; this.disabled=false; this.required=false; this.dataset={}; this.listeners={}; this.options=[]; this.controls=[]; this.checked=false; this._html=""; this.textContent=""; }
  addEventListener(type,fn) { (this.listeners[type] ||= []).push(fn); }
  emit(type,target) { (this.listeners[type]||[]).forEach(fn=>fn({target:target||this,preventDefault(){}})); }
  querySelector(selector) { if (selector==='[type="submit"]') return elements['detail-submit']; if (selector==='input, select') return this.controls[0]||null; return null; }
  querySelectorAll() { return this.controls.slice(); }
  checkValidity() { return elements['ret-tax-detailed-questions'].controls.every(control=>!control.required||String(control.value)!==''); }
  focus() {}
  set innerHTML(value) {
    this._html=String(value); this.controls=[];
    if (this.id!=='ret-tax-detailed-questions') return;
    const tags=this._html.match(/<(?:input|select)\b[^>]*>/g)||[];
    for (const tag of tags) {
      const attr=name=>{const match=tag.match(new RegExp('\\b'+name+'="([^"]*)"'));return match?match[1]:'';};
      const control=new Element(attr('id')); control.name=attr('name'); control.type=attr('type')||(tag.startsWith('<select')?'select':''); control.required=/\brequired(?:\s|>)/.test(tag); control.value=''; this.controls.push(control);
    }
  }
  get innerHTML() { return this._html; }
  get selectedOptions() { return this.options.filter(option=>option.value===this.value); }
}
const values={
  'ret-destination':'dubai','ret-home-tax-jurisdiction':'hong-kong','ret-currency':'USD',
  'ret-current-age':50,'ret-retirement-age':60,'ret-horizon':30,'ret-monthly-spending':'6,000',
  'ret-pension':'0','ret-other-income':'0','ret-rental-income':'0','ret-tax-withdrawals':'18,000',
  'ret-housing-plan':'rent','ret-property-budget':'0','ret-tax-property-use':'personal','ret-expected-return':'4'
};
const ids=['retirement-calculator','ret-destination','ret-home-tax-jurisdiction','ret-home-tax-jurisdiction-field','ret-tax-refine','ret-tax-detailed','ret-tax-detailed-form','ret-tax-detailed-questions','ret-tax-detailed-result','ret-tax-detailed-status','ret-tax-detailed-availability','detail-submit',...Object.keys(values)];
const elements=Object.fromEntries([...new Set(ids)].map(id=>[id,new Element(id,values[id]===undefined?'':values[id])]));
elements['ret-home-tax-jurisdiction'].options=[{value:'',hidden:false,disabled:false},{value:'hong-kong',hidden:false,disabled:false}];
const document={getElementById(id){return elements[id]||null;}};
global.document=document;
global.window={document,
  history:{pushState(){privacyCalls++;},replaceState(){privacyCalls++;}},
  localStorage:{getItem(){privacyCalls++;},setItem(){privacyCalls++;}},
  sessionStorage:{getItem(){privacyCalls++;},setItem(){privacyCalls++;}},
  fetch(){privacyCalls++;},dataLayer:{push(){privacyCalls++;}}
};
global.fetch=()=>{privacyCalls++;};
global.XMLHttpRequest=function(){privacyCalls++;};
global.navigator={sendBeacon(){privacyCalls++;}};
const api=require(process.argv[1]);
const input=JSON.parse(require("fs").readFileSync(0,"utf8"));
const profiles=Object.values(input.payload.supported_profiles||{});
const chosen=profiles.find(item=>item.detailed_enabled===true&&item.synthetic===false);
let initialized=false,resultRendered=false,sourceRendered=false,branchRendered=false,currencyReset=false,nativeControlEvents=0,access={};
if (chosen) {
  elements['ret-destination'].value=chosen.destination_id;
  elements['ret-home-tax-jurisdiction'].value=chosen.home_jurisdiction_id;
  const session=api.initDetailedTaxUI('retirement-calculator',input.payload);
  initialized=!!session;
  elements['ret-tax-refine'].emit('click');
  const supplied={daysInDestination:200,daysInHome:30,daysInHomePreviousYear:20,followingYearDaysKnown:'yes',daysInHomeFollowingYear:20,hongKongSettledDailyLife:'no',hongKongFixedHome:'no',hongKongWorkOrBusiness:'no',hongKongCloseFamily:'no',hasHongKongSourceIncome:false,hasHongKongProperty:false,retirementAccountClassification:'personal_investment'};
  for (let guard=0;guard<40;guard++) {
    const pending=api.nextPairQuestions(session.planningFacts(),session.answers());
    if (!pending.length) break;
    const question=pending[0], value=supplied[question.fact];
    if (value===undefined) throw new Error('Verifier lacks answer for '+question.fact);
    const control=elements['ret-tax-detailed-questions'].controls.find(item=>item.name===question.fact);
    if (!control) throw new Error('Rendered native control missing for '+question.fact);
    control.value=String(value); control.checked=true; nativeControlEvents++;
    elements['ret-tax-detailed-questions'].emit('change',control);
  }
  elements['ret-tax-detailed-form'].emit('submit');
  const markup=elements['ret-tax-detailed-result'].innerHTML;
  resultRendered=elements['ret-tax-detailed-result'].hidden===false&&markup.includes('<table')&&markup.includes('Capital needed today');
  sourceRendered=/href="https:\/\/(?:www\.)?(?:ird\.gov\.hk|centralbank\.ae|dubailand\.gov\.ae|tax\.gov\.ae|u\.ae)/.test(markup);
  branchRendered=markup.includes('UAE domestic 183-day route; not a Hong Kong resident');
  access[chosen.id]=api.profileAccess(chosen.destination_id,input.payload,{homeJurisdictionId:chosen.home_jurisdiction_id},session.answers());
  elements['ret-currency'].value='HKD'; elements['retirement-calculator'].emit('change',elements['ret-currency']);
  currencyReset=Object.keys(session.answers()).length===0&&elements['ret-tax-detailed-result'].hidden===true;
}
const probe={jurisdictions:{probe:{detailed_enabled:true,synthetic:true,runtime_bundle:{rules:{}}}}};
const controller=api.createController({questions:[{id:'probe',fact:'probeFact',control:'number',acceptedValues:{min:0,max:2,step:1,integer:true}}]});
controller.answer('probeFact',1);
process.stdout.write(JSON.stringify({
  access,privacyCalls,domInitialized:initialized,resultRendered,officialSourceLinkRendered:sourceRendered,plainBranchRendered:branchRendered,currencyReset,nativeControlEvents,
  unsupportedPairAvailable:api.profileAccess('dubai',input.payload,{homeJurisdictionId:'unsupported-home'}).available,
  selectedDestinationPresent:!!chosen&&input.destinationIds.includes(chosen.destination_id),
  syntheticProbeAvailable:api.jurisdictionAccess('probe',probe).available,controllerAnswers:controller.snapshot().answers
}));
"""
    completed = subprocess.run(
        ["node", "-e", script, str(DETAILED_TAX_UI)],
        input=json.dumps({"destinationIds": destination_ids, "payload": detailed}),
        check=True,
        capture_output=True,
        text=True,
    )
    runtime = json.loads(completed.stdout)
    return {
        "destination_count": len(destination_ids),
        "access": runtime["access"],
        "privacy_calls": int(runtime["privacyCalls"]),
        "synthetic_probe_available": bool(runtime["syntheticProbeAvailable"]),
        "controller_answers": runtime["controllerAnswers"],
        "supported_profile_count": len(detailed.get("supported_profiles", {})),
        "dom_initialized": bool(runtime["domInitialized"]),
        "result_rendered": bool(runtime["resultRendered"]),
        "official_source_link_rendered": bool(runtime["officialSourceLinkRendered"]),
        "plain_branch_rendered": bool(runtime["plainBranchRendered"]),
        "unsupported_pair_available": bool(runtime["unsupportedPairAvailable"]),
        "selected_destination_present": bool(runtime["selectedDestinationPresent"]),
        "currency_reset": bool(runtime["currencyReset"]),
        "native_control_events": int(runtime["nativeControlEvents"]),
        "claimed_profiles": list(detailed.get("supported_profiles", {}).keys()),
    }


def detailed_tax_runtime_errors(html: str) -> list[str]:
    try:
        evidence = detailed_tax_runtime_evidence(html)
    except (json.JSONDecodeError, OSError, subprocess.CalledProcessError, ValueError) as error:
        errors = [f"Detailed tax runtime verification failed: {error}"]
        try:
            claimed = _embedded_json(html, "fire-tax-detailed-data").get("supported_profiles", {})
            errors.extend(f"Detailed tax profile {profile_id} is claimed enabled but not executable" for profile_id in claimed)
        except (json.JSONDecodeError, ValueError):
            pass
        return errors
    errors: list[str] = []
    if evidence["destination_count"] <= 0:
        errors.append("Detailed tax runtime verification found no calculator destinations")
    if evidence["supported_profile_count"] <= 0:
        errors.append("Detailed tax runtime verification found no real enabled destination-and-home profile")
    if not evidence["selected_destination_present"]:
        errors.append("Detailed tax enabled profile destination is not selectable in the live calculator")
    if not evidence["dom_initialized"] or not evidence["result_rendered"]:
        errors.append("Detailed tax DOM flow did not initialize, route answers, submit and render")
    if evidence["native_control_events"] <= 0:
        errors.append("Detailed tax DOM flow did not interact with rendered native controls")
    if not evidence["currency_reset"]:
        errors.append("Detailed tax monetary answers were not cleared after a planning-currency change")
    if not evidence["official_source_link_rendered"] or not evidence["plain_branch_rendered"]:
        errors.append("Detailed tax result did not render official sources and a plain-language branch")
    if evidence["unsupported_pair_available"]:
        errors.append("Detailed tax runtime exposed an unsupported destination-and-home pair")
    if evidence["privacy_calls"] != 0:
        errors.append("Detailed tax runtime accessed URL, storage, or network APIs")
    if evidence["synthetic_probe_available"]:
        errors.append("Detailed tax runtime exposed a synthetic jurisdiction")
    if evidence["controller_answers"] != {"probeFact": 1}:
        errors.append("Detailed tax runtime did not retain an answer in memory")
    access = evidence["access"]
    for profile_id in evidence["claimed_profiles"]:
        if not isinstance(access, dict) or not access.get(profile_id, {}).get("available"):
            errors.append(f"Detailed tax profile {profile_id} is claimed enabled but not executable")
    return errors


def verify(min_sitemap_urls: int) -> list[str]:
    errors: list[str] = []
    for page in KEY_PAGES:
        if not page.exists():
            errors.append(f"Missing key page: {page.relative_to(ROOT)}")
    count = sitemap_count(ARTIFACTS / "sitemap.xml")
    if count < min_sitemap_urls:
        errors.append(f"Sitemap URL count {count} is below minimum {min_sitemap_urls}")
    for page, markers in REQUIRED_MARKERS.items():
        if not page.exists():
            continue
        text = re.sub(r"\s+", " ", page.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                errors.append(f"Missing marker {marker!r} in {page.relative_to(ROOT)}")
    finder_page = ARTIFACTS / "retirement-destination-finder" / "index.html"
    if finder_page.exists():
        errors.extend(finder_handoff_privacy_errors(finder_page.read_text(encoding="utf-8")))
    calculator_page = ARTIFACTS / "retirement-abroad-calculator" / "index.html"
    if calculator_page.exists():
        errors.extend(detailed_tax_runtime_errors(calculator_page.read_text(encoding="utf-8")))
    errors.extend(broken_local_links())
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-sitemap-urls", type=int, default=65)
    args = parser.parse_args()
    errors = verify(args.min_sitemap_urls)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Static site verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
