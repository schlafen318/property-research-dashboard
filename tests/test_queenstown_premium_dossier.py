import json
import re
import unittest
from pathlib import Path

from src.premium_destination_dossiers import DECISION_DIMENSION_KEYS, PREMIUM_DESTINATION_DOSSIERS, get_premium_dossier, validate_premium_dossier

ROOT = Path(__file__).parents[1]
DESTINATION_ID = "queenstown"
FX = 1.1699 / 1.9541


class QueenstownDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_sixteen_reviewed_dossiers(self):
        self.assertEqual(16, len(PREMIUM_DESTINATION_DOSSIERS))
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self):
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, {key for lens in self.spec.lenses for key in lens.dimension_keys})
        self.assertEqual((3, 4, 3, 8, 2), (len(self.spec.market_anchors), len(self.spec.micro_locations), len(self.spec.images), len(self.spec.checklist), len(self.spec.orientation_groups)))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_locally_specific_and_decision_grade(self):
        prose = " ".join([self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
                          *(p for lens in self.spec.lenses for p in lens.paragraphs), self.spec.micro_locations_intro])
        for term in ("Frankton", "Queenstown Hill", "Fernhill", "Arrowtown", "Lake Hayes", "Jacks Point"):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        for pattern in (r"overseas|consent|residence", r"visitor accommodation|short.?stay|rental", r"flood|landslide|rockfall|fire", r"hospital|health|emergency", r"resale|exit|buyer pool"):
            self.assertRegex(prose.lower(), pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(x["url"] for x in self.spec.references)
        for fragment in ("linz.govt.nz", "immigration.govt.nz", "qldc.govt.nz", "healthnz.govt.nz", "orc.govt.nz", "nzta.govt.nz", "queenstownairport.co.nz", "qv.co.nz", "ird.govt.nz", "settled.govt.nz"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_evidence_ledger_is_direct_and_maintainable(self):
        ledger = (ROOT / "docs/research/queenstown-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 14)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        for trigger in ("ownership", "residence", "tax", "planning", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())

    def test_market_anchors_are_explicit_rating_values(self):
        evidence = " ".join(" ".join(str(v) for v in x.values()) for x in self.spec.market_anchors)
        for value in ("NZ$1,711,114", "NZ$2,171,809", "NZ$3,025,016"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"rating|capital value|not a valuation")
        self.assertIn("2024", evidence)

    def test_atlas_reads_are_concise_and_local(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(read.split()), 12)
                self.assertLessEqual(len(read.split()), 36)
                self.assertRegex(read, r"Queenstown|Frankton|Arrowtown|Jacks Point|Fernhill|Lake Hayes|Wakatipu")


class QueenstownListingTests(unittest.TestCase):
    def test_three_current_direct_nzd_observations_are_complete(self):
        rows = [x for x in json.loads((ROOT / "data/listings.json").read_text()) if x["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual({"Frankton Road lakefront apartment", "Hanley's Farm home and income", "Queenstown Hill new-build house"}, {x["listing_name"] for x in rows})
        self.assertEqual({
            "https://www.realestate.co.nz/43093321/residential/sale/unit-606-327-frankton-road-queenstown-central?lid=jyzkx2cbid2g",
            "https://www.listed.co.nz/property/5200",
            "https://www.realestate.co.nz/43060560/residential/sale/79-middleton-road-queenstown-hill",
        }, {x["source_url"] for x in rows})
        for row in rows:
            self.assertEqual("NZD", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertIn("1 EUR = 1.1699 USD and 1 EUR = 1.9541 NZD", row["fx_basis"])
            self.assertIn("floor area", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        self.assertEqual({68, 237, 322}, {row["size_m2"] for row in rows})

    def test_shared_price_basis_is_transparent_and_current(self):
        destination = next(x for x in json.loads((ROOT / "data/destinations.json").read_text()) if x["id"] == DESTINATION_ID)
        self.assertEqual(6500.0, destination["usd_per_m2"])
        self.assertEqual("$6,500", destination["quick_metrics"]["usd_m"])
        for text in ("NZ$1,941,732", "QV", "asking observations", "0.59869"):
            self.assertIn(text, destination["price_basis"])
        retirement = next(x for x in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"] if x["destination_id"] == DESTINATION_ID)
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=12)
        self.assertEqual(1065668, retirement["property"]["representative_price_usd"])
        self.assertIn("asking observations", retirement["property"]["price_basis"])
        self.assertEqual(0.005, retirement["property"]["acquisition_cost_rate"])
        self.assertIn("0.5% planning allowance", retirement["property"]["acquisition_cost_basis"])
        self.assertIn("no stamp-duty percentage", retirement["property"]["acquisition_cost_basis"])
        source_urls = {source["url"] for source in retirement["sources"]}
        self.assertIn("https://www.linz.govt.nz/guidance/overseas-investment/ways-invest/pathways-migrants-and-visa-holders/investing-residential-land-over-5-million", source_urls)
        self.assertIn("https://www.settled.govt.nz/blog/buying-your-first-home-heres-what-you-need-to-know/", source_urls)


class QueenstownRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.build_unified_app import build_destination_page, consolidate_destination
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(x) for x in destinations]
        cls.html = build_destination_page(next(x for x in enriched if x["id"] == DESTINATION_ID), listings, enriched, [])

    def test_page_uses_premium_sequence_and_new_zealand_handoff(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{x}"') for x in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")]
        self.assertEqual(sorted(positions), positions)
        for text in ("Queenstown through five destination lenses", "Here’s how Queenstown scores", "Compare Queenstown with the full Atlas.", "/countries/new-zealand-property/", "/retirement-abroad-calculator/"):
            self.assertIn(text, self.html)

    def test_country_handoff_is_bidirectional(self):
        from src.build_unified_app import COUNTRY_HUBS, build_country_comparison_page, build_country_hub_page
        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "new-zealand-property")
        self.assertEqual("New Zealand", hub["country"])
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn("New Zealand Property Guide for Foreign Buyers", html)
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        for text in (
            "Who can buy a home",
            "Investor-visa home pathway",
            "Residence is a separate decision",
            "purchase price of more than NZ$5 million",
            "land purchase and construction prices must together exceed NZ$5 million",
            "https://www.linz.govt.nz/guidance/overseas-investment/buying-residential-property-live",
            "https://www.linz.govt.nz/guidance/overseas-investment/ways-invest/pathways-migrants-and-visa-holders/investing-residential-land-over-5-million",
            "https://www.immigration.govt.nz/visas/temporary-retirement-visitor-visa/",
        ):
            self.assertIn(text, html)
        comparison = build_country_comparison_page(destinations, [])
        self.assertIn('<span>1 destination</span>\n              <h3><a href="/countries/new-zealand-property/">New Zealand</a></h3>', comparison)

    def test_investor_pathway_copy_distinguishes_existing_home_from_land_and_build(self):
        spec = get_premium_dossier(DESTINATION_ID)
        copy = " ".join([*spec.verdict_paragraphs, *spec.score_reads.values()])
        self.assertIn("existing dwelling with a purchase price of more than NZ$5 million", copy)
        self.assertIn("land purchase and construction prices must together exceed NZ$5 million", copy)

    def test_images_tables_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/queenstown-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        for count, marker in ((10, 'class="premium-score-row"'), (3, 'class="premium-listing-row"'), (3, 'class="premium-market-anchor"'), (2, 'class="premium-orientation-group"')):
            self.assertEqual(count, self.html.count(marker))
        self.assertIn("asking evidence—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)
        self.assertIn("<th>Area / basis</th>", self.html)

    def test_quality_review_uses_canonical_scorecard_fields(self):
        review = (ROOT / "docs/research/queenstown-quality-review.md").read_text()
        for weight in ("| Decision usefulness | 15 |", "| Evidence and accuracy | 25 |", "| Atlas model integrity | 15 |", "| Property and location evidence | 15 |", "| Editorial quality | 10 |", "| Design, mobile, and accessibility | 10 |", "| SEO and trust | 5 |", "| Build and maintenance | 5 |"):
            self.assertIn(weight, review)
        for field in ("Reviewer:", "Approval date:", "Console warnings: 0"):
            self.assertIn(field, review)


if __name__ == "__main__":
    unittest.main()
