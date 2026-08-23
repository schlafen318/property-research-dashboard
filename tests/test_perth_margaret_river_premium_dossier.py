import json
import html as html_module
import re
import unittest
from pathlib import Path

from PIL import Image

from src.premium_destination_dossiers import (
    DECISION_DIMENSION_KEYS,
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "perth-margaret-river"


class PerthMargaretRiverDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_perth_margaret_river(self) -> None:
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self) -> None:
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual((None, 1, 2), self.spec.property_anchor_indexes)
        self.assertEqual(4, len(self.spec.micro_locations))
        self.assertEqual(3, len(self.spec.images))
        self.assertEqual(8, len(self.spec.checklist))
        self.assertEqual(2, len(self.spec.orientation_groups))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_locally_specific_and_decision_grade(self) -> None:
        prose = " ".join([
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in (
            "Perth", "East Perth", "South Perth", "Mount Pleasant",
            "Fremantle", "Margaret River", "Prevelly", "Gnarabup",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"airport|terminal|drive|coach")
        self.assertRegex(prose.lower(), r"short-term|stra|planning|register")
        self.assertRegex(prose.lower(), r"bushfire|coastal|insurance|evacuation")
        self.assertRegex(prose.lower(), r"hospital|emergency|health|medicare")
        self.assertRegex(prose.lower(), r"resale|exit|strata|manager")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_ownership_and_both_operating_markets(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "foreigninvestment.gov.au", "ato.gov.au", "immi.homeaffairs.gov.au",
            "servicesaustralia.gov.au", "wa.gov.au", "planning.wa.gov.au",
            "amrshire.wa.gov.au", "landgate.wa.gov.au", "dfes.wa.gov.au",
            "health.wa.gov.au", "perthairport.com.au", "rba.gov.au",
            "transfer-duty-assessment",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-23", self.spec.date_reviewed)
        self.assertIn("23 February 2027", self.spec.references_intro)
        dossier_copy = " ".join(self.spec.verdict_paragraphs) + " " + " ".join(
            paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs
        )
        self.assertIn("30 June 2029", dossier_copy)
        self.assertRegex(dossier_copy.lower(), r"does not (?:create|provide).*visa|property ownership does not")
        self.assertRegex(dossier_copy.lower(), r"90[^.]{0,30}night")
        self.assertNotRegex(dossier_copy.lower(), r"uniform wa short-term|one wa short-term rule")
        ownership_lens = next(
            lens for lens in self.spec.lenses if "ownership_clarity" in lens.dimension_keys
        )
        ownership_copy = " ".join(ownership_lens.paragraphs).lower()
        for term in ("bushfire", "coastal", "insurance"):
            self.assertIn(term, ownership_copy)
        self.assertNotIn("flood", " ".join(self.spec.checklist).lower())
        retirement_lens = next(
            lens for lens in self.spec.lenses if "retirement_fit" in lens.dimension_keys
        )
        self.assertNotIn("on-call doctor", " ".join(retirement_lens.paragraphs).lower())

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs/research/perth-margaret-river-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 18)
        self.assertGreaterEqual(ledger.count("https://"), 20)
        for trigger in ("foreign investment", "tax", "planning", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())
        self.assertIn("29 August 2023", ledger)

    def test_generated_images_have_a_publication_provenance_record(self) -> None:
        provenance = (ROOT / "docs/research/perth-margaret-river-image-provenance.md").read_text()
        for image in self.spec.images:
            filename = Path(image.src).name
            self.assertIn(filename, provenance)
            with Image.open(ROOT / "src/site_assets" / filename) as rendered:
                self.assertEqual((1672, 941), rendered.size)
        for field in (
            "Generation tool", "Generation date", "Prompt", "Generation output",
            "Publication-rights basis", "Visual approval",
        ):
            self.assertIn(field, provenance)
        self.assertEqual(3, provenance.count("/Users/steph-tmp/.codex/generated_images/"))
        self.assertNotRegex(provenance, r"(?i)pending|unknown|unverified")

    def test_market_anchors_are_scoped_public_signals_not_valuations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        self.assertRegex(evidence.lower(), r"median")
        self.assertRegex(evidence.lower(), r"2024|2025|2026")
        self.assertRegex(evidence.lower(), r"perth|south perth|margaret river")
        self.assertRegex(evidence.lower(), r"not a valuation|public market")
        self.assertRegex(evidence.lower(), r"house|unit|apartment")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Perth|Fremantle|Margaret River|Prevelly|Gnarabup|WA")


class PerthMargaretRiverDataTests(unittest.TestCase):
    def test_australia_mortgage_profile_is_explicit_not_assumed(self) -> None:
        profiles = json.loads((ROOT / "data/mortgage_profiles.json").read_text())["countries"]
        profile = profiles["Australia"]
        self.assertEqual("research_incomplete", profile["availability"])
        self.assertIsNone(profile["maximum_ltv"])
        self.assertEqual(["AUD"], profile["loan_currencies"])
        self.assertRegex(" ".join(profile["conditions"]).lower(), r"foreign-investment eligibility|non-resident")

    def test_three_current_direct_aud_observations_are_complete(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("AUD", row["local_currency"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertEqual(0.7145, row["fx_rate_to_usd"])
            self.assertIn("area_basis", row)
            self.assertNotRegex(row["area_basis"], r"(?i)estimate")
            self.assertRegex(row["area_basis"], r"(?i)internal|living area")
            self.assertNotRegex(row["area_basis"], r"(?i)total area|building size")
            self.assertAlmostEqual(row["local_price"] * 0.7145, row["usd_price"], delta=1)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
            self.assertNotRegex(row["source_url"], r"realestate\.com\.au/(?:buy|new-apartments)/?$|domain\.com\.au/sale/?$")

        east_perth = next(row for row in rows if "Garden Towers" in row["listing_name"])
        self.assertEqual(1840000, east_perth["local_price"])
        self.assertEqual(1314680, east_perth["usd_price"])
        self.assertIn("construction underway", east_perth["note"].lower())
        self.assertIn("mid–late 2026", east_perth["note"])

        como = next(row for row in rows if "Coterie" in row["listing_name"])
        self.assertEqual(1473390, como["local_price"])
        self.assertEqual(110, como["size_m2"])
        self.assertEqual(
            "https://www.joneshq.com.au/property/3-bedroom-apartment-in-como-nearing-completion/",
            como["source_url"],
        )
        self.assertIn("110 m²", como["area_basis"])
        self.assertIn("completion", como["note"].lower())

        margaret_river = next(row for row in rows if "Sandstone" in row["listing_name"])
        self.assertEqual(878300, margaret_river["local_price"])
        self.assertEqual(147.01, margaret_river["size_m2"])
        self.assertIn("147.01 m²", margaret_river["area_basis"])
        self.assertIn("193.05 m²", margaret_river["note"])
        self.assertIn("garage", margaret_river["note"].lower())

    def test_shared_score_price_yield_and_calculator_are_reconciled(self) -> None:
        from src.build_unified_app import consolidate_destination

        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        enriched = consolidate_destination(destination)
        self.assertEqual(3.61, destination["overall_score"])
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertEqual(9600, destination["usd_per_m2"])
        self.assertIn("three direct", destination["price_basis"])
        self.assertIn("asking", destination["price_basis"])
        self.assertIn("living/internal", destination["price_basis"])
        self.assertNotIn("mixed", destination["price_basis"].lower())
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])
        costs = json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
        cost = next(row for row in costs if row["destination_id"] == DESTINATION_ID)
        self.assertIn("three direct", cost["property"]["price_basis"])
        self.assertEqual(destination["representative_price_usd"], cost["property"]["representative_price_usd"])
        self.assertEqual(1052737.155, cost["property"]["representative_price_usd"])
        self.assertEqual(0.115, cost["property"]["acquisition_cost_rate"])
        listings = json.loads((ROOT / "data/listings.json").read_text())
        regional_listing = next(item for item in listings if "Sandstone 195" in item["listing_name"])
        self.assertIn("from-price", regional_listing["note"])
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertIn("from A$878,300", spec.listings_intro)
        value_lens = next(lens for lens in spec.lenses if "value_entry" in lens.dimension_keys)
        self.assertIn("starting price", " ".join(value_lens.paragraphs).lower())
        property_source = next(
            source for source in cost["sources"]
            if source["metric_supported"] == "Representative property acquisition benchmark"
        )
        self.assertIn("three direct asking observations", property_source["name"].lower())
        self.assertNotIn("realestate.com.au", property_source["name"].lower())
        self.assertNotIn("//", property_source["url"].split("://", 1)[1])
        self.assertIn("Como", property_source["notes"])
        self.assertNotIn("Mount Pleasant", property_source["notes"])


class PerthMargaretRiverRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_handoffs(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Perth / Margaret River through five destination lenses", self.html)
        self.assertIn("Here’s how Perth / Margaret River scores", self.html)
        self.assertIn("Compare Perth / Margaret River with the full Atlas.", self.html)
        self.assertIn("/countries/australia-property/", self.html)
        self.assertIn("/retirement-abroad-calculator/", self.html)

    def test_images_tables_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/perth-margaret-river-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{html_module.escape(image.alt, quote=True)}"', self.html)
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-property-record"'))
        self.assertNotIn('class="premium-listing-row"', self.html)
        self.assertEqual(2, self.html.count('class="premium-local-comparison"'))
        self.assertEqual(3, self.html.count("View current listing"))
        listings_section = self.html.split('id="listings"', 1)[1].split('</section>', 1)[0]
        self.assertNotIn("Captured", listings_section)
        self.assertNotIn("confidence", listings_section.lower())
        self.assertNotIn("Official market anchors", self.html)
        self.assertEqual(1, self.html.count('class="premium-market-context"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("public market signals—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)

    def test_australia_country_handoff_is_substantive_and_bidirectional(self) -> None:
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "australia-property")
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        self.assertIn("gold-coast-sunshine-coast", hub["destination_ids"])
        self.assertIn("sydney-melbourne", hub["destination_ids"])
        self.assertGreaterEqual(len(hub["country_rules"]), 4)
        self.assertTrue(any("established" in rule["text"].lower() for rule in hub["country_rules"]))
        source_urls = " ".join(source["url"] for source in hub["primary_sources"])
        for domain in ("foreigninvestment.gov.au", "ato.gov.au", "immi.homeaffairs.gov.au", "wa.gov.au"):
            self.assertIn(domain, source_urls)
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        briefing = html.split('aria-label="Country briefing"', 1)[1].split('</section>', 1)[0]
        self.assertIn(f'href="/destinations/{DESTINATION_ID}/"', briefing)
        next_step = html.split('class="buyer-next-step"', 1)[1].split('</section>', 1)[0]
        self.assertIn(f'href="/destinations/{DESTINATION_ID}/"', next_step)

    def test_quality_review_uses_canonical_scorecard_fields(self) -> None:
        review = (ROOT / "docs/research/perth-margaret-river-quality-review.md").read_text()
        for weight in (
            "| Decision usefulness | 15 |", "| Evidence and accuracy | 25 |",
            "| Atlas model integrity | 15 |", "| Property and location evidence | 15 |",
            "| Editorial quality | 10 |", "| Design, mobile, and accessibility | 10 |",
            "| SEO and trust | 5 |", "| Build and maintenance | 5 |",
        ):
            self.assertIn(weight, review)
        for field in ("Reviewer:", "Approval date:", "Console warnings:"):
            self.assertIn(field, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet approved")
        self.assertIn("Result: 100/100", review)


if __name__ == "__main__":
    unittest.main()
