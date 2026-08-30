import json
import re
import unittest
from pathlib import Path

from src.premium_destination_dossiers import (
    DECISION_DIMENSION_KEYS,
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "chamonix"
EUR_USD = 1.1699


class ChamonixDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_and_bounded_contract(self):
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual(4, len(self.spec.micro_locations))
        self.assertEqual(3, len(self.spec.images))
        self.assertEqual(8, len(self.spec.checklist))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_local_decision_grade_and_bounded(self):
        prose = " ".join([
            self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
            *(p for lens in self.spec.lenses for p in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in ("Chamonix Centre", "Les Praz", "Argentière", "Les Houches"):
            self.assertIn(term, prose)
        for pattern in (
            r"long-stay|residence", r"change-of-use|registration", r"copropri[eé]t[eé]",
            r"DPE|energy", r"hospital|healthcare", r"Mont-Blanc Express|bus",
            r"avalanche|flood|hazard", r"resale|exit|buyer pool",
        ):
            self.assertRegex(prose, pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_and_ledger_cover_high_stakes_claims(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "france-visas.gouv.fr", "ameli.fr", "chamonix.fr", "service-public.fr",
            "georisques.gouv.fr", "hpmb.fr", "ter.sncf.com", "notaires.fr",
            "ecb.europa.eu", "proprietes.lefigaro.fr",
        ):
            self.assertIn(fragment, urls)
        ledger = (ROOT / "docs/research/chamonix-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 16)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        self.assertIn("/urgences-chamonix/", urls)
        self.assertIn("11 July to 30 August 2026", " ".join(
            paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs
        ))


class ChamonixListingAndDataTests(unittest.TestCase):
    def test_three_current_direct_observations_are_reconciled(self):
        rows = [r for r in json.loads((ROOT / "data/listings.json").read_text()) if r["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual({"Chamonix Savoy one-bedroom apartment", "Les Houches three-bedroom apartment", "Les Praz four-bedroom chalet"}, {r["listing_name"] for r in rows})
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("Propriétés Le Figaro", row["source_name"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertIn("1.1699", row["fx_basis"])
            self.assertTrue(row["source_url"].startswith("https://proprietes.lefigaro.fr/annonces/"))
            self.assertIn("surface", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * EUR_USD, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)

        houches = next(row for row in rows if row["listing_name"].startswith("Les Houches"))
        self.assertEqual(75, houches["size_m2"])
        self.assertIn("Carrez", houches["area_basis"])
        self.assertEqual("Low", houches["confidence"])
        for conflict in ("8 lots", "not subject to copropriété", "20 lots"):
            self.assertIn(conflict, houches["note"])

    def test_shared_score_price_and_yield_are_reconciled(self):
        from src.build_unified_app import consolidate_destination
        destination = next(r for r in json.loads((ROOT / "data/destinations.json").read_text()) if r["id"] == DESTINATION_ID)
        enriched = consolidate_destination(destination)
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertIn("Notaires", destination["price_basis"])
        self.assertIn("9,760", destination["price_basis"])
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[–-]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])


class ChamonixRenderingAndHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.build_unified_app import build_destination_page, consolidate_destination
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(r) for r in destinations]
        destination = next(r for r in enriched if r["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_premium_render_images_and_handoff(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        self.assertIn("Chamonix through five destination lenses", self.html)
        self.assertEqual(3, self.html.count('src="/assets/chamonix-'))
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertIn('premium-desktop-record-table', self.html)
        self.assertIn("/countries/france-property/", self.html)
        for asset in (
            "/assets/chamonix-valley-life.webp",
            "/assets/chamonix-winter-access.webp",
            "/assets/chamonix-building-governance.webp",
        ):
            self.assertEqual(1, self.html.count(f'src="{asset}"'), asset)
            self.assertTrue((ROOT / "src" / "site_assets" / Path(asset).name).exists(), asset)

    def test_france_hub_is_substantive_and_bidirectional(self):
        from src.build_unified_app import COUNTRY_HUBS, SEO_PAGES, build_country_hub_page
        hub = next(item for item in COUNTRY_HUBS if item["country"] == "France")
        self.assertGreaterEqual(len(hub["country_rules"]), 3)
        self.assertEqual({"annecy", "chamonix"}, set(hub["destination_ids"]))
        urls = " ".join(item["url"] for item in hub["primary_sources"])
        self.assertIn("france-visas.gouv.fr", urls)
        self.assertIn("service-public.fr", urls)
        html = build_country_hub_page(hub, json.loads((ROOT / "data/destinations.json").read_text()), SEO_PAGES)
        self.assertIn("/destinations/annecy/", html)
        self.assertIn("/destinations/chamonix/", html)

    def test_quality_review_uses_canonical_100_point_scorecard(self):
        review = (ROOT / "docs/research/chamonix-quality-review.md").read_text()
        for field in (
            "Reviewer:", "Approval date:", "Decision usefulness", "Evidence and accuracy",
            "Atlas model integrity", "Property and location evidence", "Editorial quality",
            "Design, mobile, and accessibility", "SEO and trust", "Build and maintenance",
            "Console warnings:", "100/100",
        ):
            self.assertIn(field, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet approved")


if __name__ == "__main__":
    unittest.main()
