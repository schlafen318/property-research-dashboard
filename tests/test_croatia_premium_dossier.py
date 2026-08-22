import json
import re
import unittest
from pathlib import Path

from src.premium_destination_dossiers import DECISION_DIMENSION_KEYS, PREMIUM_DESTINATION_DOSSIERS, get_premium_dossier, validate_premium_dossier

ROOT = Path(__file__).parents[1]
DESTINATION_ID = "croatia-istria-dalmatia"


class CroatiaDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_fifteen_reviewed_dossiers(self):
        self.assertEqual(15, len(PREMIUM_DESTINATION_DOSSIERS))
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
        for term in ("Split", "Trogir", "Kaštela", "Rovinj", "Pula", "Poreč", "Hvar", "Brač"):
            with self.subTest(term=term): self.assertIn(term, prose)
        for pattern in (r"airport|flight|ferry|island", r"tourist|categoris|rental", r"flood|fire|heat|water", r"hospital|health|emergency", r"resale|exit|season|operator"):
            self.assertRegex(prose.lower(), pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(x["url"] for x in self.spec.references)
        for fragment in ("mup.gov.hr", "gov.hr", "uredjenazemlja.hr", "portal-ispu.gov.hr", "mint.gov.hr", "hzzo.hr", "voda.hr", "hvz.gov.hr", "split-airport.hr", "mpgi.gov.hr"):
            with self.subTest(fragment=fragment): self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)
        self.assertIn("3,881,186", " ".join(p for lens in self.spec.lenses for p in lens.paragraphs))

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self):
        ledger = (ROOT / "docs/research/croatia-istria-dalmatia-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 14)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        for trigger in ("residence", "tax", "planning", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())

    def test_three_market_anchors_are_bounded_completed_evidence(self):
        evidence = " ".join(" ".join(str(v) for v in x.values()) for x in self.spec.market_anchors)
        for value in ("€2,743/m²", "€4,068/m²", "€3,921/m²"): self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"transaction|completed|median")
        self.assertIn("2025", evidence)

    def test_atlas_reads_are_concise_and_locally_specific(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(read.split()), 12)
                self.assertLessEqual(len(read.split()), 36)
                self.assertRegex(read, r"Croatia|Split|Trogir|Kaštela|Rovinj|Pula|Poreč|Hvar|Brač|Istria|Dalmatia")


class CroatiaListingTests(unittest.TestCase):
    def test_three_current_direct_eur_observations_are_complete(self):
        rows = [x for x in json.loads((ROOT / "data/listings.json").read_text()) if x["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual({"Rovinjsko Selo one-bedroom apartment", "Split prime apartment", "Hvar pool villa"}, {x["listing_name"] for x in rows})
        self.assertEqual({
            "https://www.opereta.hr/en/real-estate/apartment/121643-sale-apartment-2-room-istarska-zupanija-rovinjsko-selo",
            "https://www.croatiapropertysales.com/hr/hrvatska-split-apartman-na-prodaju-5802/",
            "https://www.croatiapropertysales.com/croatia-hvar-villa-for-sale-5399/",
        }, {x["source_url"] for x in rows})
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertIn("1 EUR = 1.1699 USD", row["fx_basis"])
            self.assertIn("living", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * 1.1699, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        self.assertEqual({58.32, 79, 170}, {row["size_m2"] for row in rows})

    def test_shared_price_basis_uses_current_completed_evidence(self):
        destination = next(x for x in json.loads((ROOT / "data/destinations.json").read_text()) if x["id"] == DESTINATION_ID)
        self.assertEqual(3900.0, destination["usd_per_m2"])
        self.assertEqual("$3,900", destination["quick_metrics"]["usd_m"])
        for text in ("€3,333/m²", "completed", "2025", "1.1699"):
            self.assertIn(text, destination["price_basis"])


class CroatiaRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.build_unified_app import build_destination_page, consolidate_destination
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(x) for x in destinations]
        cls.html = build_destination_page(next(x for x in enriched if x["id"] == DESTINATION_ID), listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_local_copy(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{x}"') for x in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")]
        self.assertEqual(sorted(positions), positions)
        for text in ("Croatia through five destination lenses", "Here’s how Croatia scores", "Compare Croatia with the full Atlas.", "/countries/croatia-property/", "/retirement-abroad-calculator/"):
            self.assertIn(text, self.html)

    def test_country_handoff_points_to_a_rendered_croatia_hub(self):
        from src.build_unified_app import COUNTRY_HUBS, build_country_comparison_page, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "croatia-property")
        self.assertEqual("Croatia", hub["country"])
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn("Croatia Property Guide for Foreign Buyers", html)
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        comparison = build_country_comparison_page(destinations, [])
        self.assertIn('<span>1 destination</span>\n              <h3><a href="/countries/croatia-property/">Croatia</a></h3>', comparison)

    def test_images_tables_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/croatia-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        for count, marker in ((10, 'class="premium-score-row"'), (3, 'class="premium-listing-row"'), (3, 'class="premium-market-anchor"'), (2, 'class="premium-orientation-group"')):
            self.assertEqual(count, self.html.count(marker))
        self.assertIn("asking evidence—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)
        self.assertIn("<th>Area / basis</th>", self.html)

    def test_quality_review_uses_canonical_scorecard_and_named_approval(self):
        review = (ROOT / "docs/research/croatia-istria-dalmatia-quality-review.md").read_text()
        for weight in ("| Decision usefulness | 15 |", "| Evidence and accuracy | 25 |", "| Atlas model integrity | 15 |", "| Property and location evidence | 15 |", "| Editorial quality | 10 |", "| Design, mobile, and accessibility | 10 |", "| SEO and trust | 5 |", "| Build and maintenance | 5 |"):
            self.assertIn(weight, review)
        for field in ("Reviewer:", "Approval date:", "Console warnings:"):
            self.assertIn(field, review)


if __name__ == "__main__":
    unittest.main()
