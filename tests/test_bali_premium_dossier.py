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
DESTINATION_ID = "bali"
USD_IDR = 17705.0


class BaliDossierContractTests(unittest.TestCase):
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
        for term in ("Sanur", "Ubud", "Canggu", "Uluwatu"):
            self.assertIn(term, prose)
        for pattern in (
            r"Hak Pakai|Right to Use", r"leasehold|lease term", r"immigration|E33F",
            r"KBLI|licen[cs]", r"traffic|car", r"hospital|healthcare",
            r"flood|tsunami|hazard", r"resale|exit|terminal value",
        ):
            self.assertRegex(prose, pattern)
        self.assertIn("10% final income tax", prose)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_and_ledger_cover_high_stakes_claims(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "jdih.atrbpn.go.id", "imigrasi.go.id", "oss.go.id", "pajak.go.id",
            "bi.go.id", "bali.bps.go.id", "bpbd.baliprov.go.id",
            "sik-kbs.baliprov.go.id", "injourneyairports.id",
        ):
            self.assertIn(fragment, urls)
        ledger = (ROOT / "docs/research/bali-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 16)
        self.assertGreaterEqual(ledger.count("https://"), 18)


class BaliListingAndDataTests(unittest.TestCase):
    def test_three_current_direct_leasehold_observations_are_reconciled(self):
        rows = [r for r in json.loads((ROOT / "data/listings.json").read_text()) if r["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual({"Sanur beachside leasehold villa", "Canggu Batu Mejan leasehold villa", "Ubud six-bedroom leasehold villa"}, {r["listing_name"] for r in rows})
        for row in rows:
            self.assertEqual("IDR", row["local_currency"])
            self.assertEqual("Rumah123", row["source_name"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertIn("17,705", row["fx_basis"])
            self.assertIn("portal-stated building area", row["area_basis"].lower())
            self.assertIn("lease", row["note"].lower())
            self.assertAlmostEqual(row["local_price"] / USD_IDR, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)

        canggu = next(row for row in rows if row["listing_name"] == "Canggu Batu Mejan leasehold villa")
        self.assertIn("seller contradiction", canggu["note"].lower())
        self.assertIn("1 August 2052", canggu["note"])
        self.assertIn("executed lease", canggu["note"].lower())

    def test_shared_score_and_price_basis_are_reconciled(self):
        from src.build_unified_app import consolidate_destination
        destination = next(r for r in json.loads((ROOT / "data/destinations.json").read_text()) if r["id"] == DESTINATION_ID)
        enriched = consolidate_destination(destination)
        self.assertEqual(3.56, destination["overall_score"])
        self.assertEqual(3.56, enriched["decision_score"])
        self.assertIn("median of three", destination["price_basis"].lower())
        self.assertIn("leasehold", destination["price_basis"].lower())
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[–-]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])


class BaliRenderingAndHandoffTests(unittest.TestCase):
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
        self.assertIn("Bali through five destination lenses", self.html)
        self.assertEqual(3, self.html.count('src="/assets/bali-'))
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertIn('class="premium-listing-table premium-card-table premium-desktop-record-table"', self.html)
        self.assertIn("/countries/indonesia-property/", self.html)

    def test_indonesia_hub_is_substantive_and_bidirectional(self):
        from src.build_unified_app import COUNTRY_HUBS, SEO_PAGES, build_country_hub_page
        hub = next(item for item in COUNTRY_HUBS if item["country"] == "Indonesia")
        self.assertGreaterEqual(len(hub["country_rules"]), 3)
        urls = " ".join(item["url"] for item in hub["primary_sources"])
        self.assertIn("atrbpn.go.id", urls)
        self.assertIn("imigrasi.go.id", urls)
        self.assertIn("pajak.go.id", urls)
        html = build_country_hub_page(hub, json.loads((ROOT / "data/destinations.json").read_text()), SEO_PAGES)
        self.assertIn("/destinations/bali/", html)

    def test_quality_review_uses_canonical_100_point_scorecard(self):
        review = (ROOT / "docs/research/bali-quality-review.md").read_text()
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
