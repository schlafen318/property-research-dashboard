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
        "central tax-adjusted target",
        "Favorable–adverse target range",
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
global.window={
  history:{pushState(){privacyCalls++;},replaceState(){privacyCalls++;}},
  localStorage:{getItem(){privacyCalls++;},setItem(){privacyCalls++;}},
  sessionStorage:{getItem(){privacyCalls++;},setItem(){privacyCalls++;}},
  fetch(){privacyCalls++;}
};
const api=require(process.argv[1]);
const input=JSON.parse(require("fs").readFileSync(0,"utf8"));
const access=Object.fromEntries(input.destinationIds.map(id=>[id,api.jurisdictionAccess(id,input.payload)]));
const probe={jurisdictions:{probe:{detailed_enabled:true,synthetic:true,runtime_bundle:{rules:{}}}}};
const controller=api.createController({questions:[{id:"probe",fact:"probeFact",control:"number",acceptedValues:{min:0,max:2,step:1,integer:true}}]});
controller.answer("probeFact",1);
process.stdout.write(JSON.stringify({
  access,
  privacyCalls,
  syntheticProbeAvailable:api.jurisdictionAccess("probe",probe).available,
  controllerAnswers:controller.snapshot().answers
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
        "claimed_jurisdictions": list(detailed.get("jurisdictions", {}).keys()),
    }


def detailed_tax_runtime_errors(html: str) -> list[str]:
    try:
        evidence = detailed_tax_runtime_evidence(html)
    except (json.JSONDecodeError, OSError, subprocess.CalledProcessError, ValueError) as error:
        return [f"Detailed tax runtime verification failed: {error}"]
    errors: list[str] = []
    if evidence["destination_count"] <= 0:
        errors.append("Detailed tax runtime verification found no calculator destinations")
    if evidence["privacy_calls"] != 0:
        errors.append("Detailed tax runtime accessed URL, storage, or network APIs")
    if evidence["synthetic_probe_available"]:
        errors.append("Detailed tax runtime exposed a synthetic jurisdiction")
    if evidence["controller_answers"] != {"probeFact": 1}:
        errors.append("Detailed tax runtime did not retain an answer in memory")
    access = evidence["access"]
    for jurisdiction_id in evidence["claimed_jurisdictions"]:
        if not isinstance(access, dict) or not access.get(jurisdiction_id, {}).get("available"):
            errors.append(f"Detailed tax jurisdiction {jurisdiction_id} is claimed enabled but not executable")
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
