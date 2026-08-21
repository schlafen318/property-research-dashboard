import unittest
import json
import re
from pathlib import Path

from src.premium_destination_dossiers import (
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


class PremiumDossierContractTests(unittest.TestCase):
    def test_only_fukuoka_uses_the_premium_registry(self) -> None:
        self.assertEqual({"fukuoka-itoshima"}, set(PREMIUM_DESTINATION_DOSSIERS))
        self.assertIsNotNone(get_premium_dossier("fukuoka-itoshima"))
        self.assertIsNone(get_premium_dossier("valencia"))

    def test_fukuoka_spec_has_the_complete_bounded_contract(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertIsNotNone(spec)
        validate_premium_dossier(spec)
        self.assertEqual(5, len(spec.lenses))
        self.assertEqual(
            10,
            len({key for lens in spec.lenses for key in lens.dimension_keys}),
        )
        self.assertLessEqual(len(spec.nav_items), 7)
        self.assertEqual(3, len(spec.images))
        self.assertEqual("sources", spec.nav_items[-1][0])


class PremiumDossierContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier("fukuoka-itoshima")
        self.assertIsNotNone(self.spec)

    def test_references_cover_the_high_stakes_source_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        required_fragments = (
            "mofa.go.jp",
            "mof.go.jp",
            "nta.go.jp",
            "mlit.go.jp",
            "city.fukuoka.lg.jp",
            "city.itoshima.lg.jp",
            "fukuoka-airport.jp",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)

    def test_each_lens_is_destination_specific_and_editorial_length_is_bounded(self) -> None:
        for lens in self.spec.lenses:
            prose = " ".join(lens.paragraphs)
            self.assertRegex(prose, r"Fukuoka|Itoshima")
            self.assertGreaterEqual(len(lens.paragraphs), 3)

        prose_fields = [
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
            self.spec.references_intro,
        ]
        words = re.findall(r"\b[\w’'-]+\b", " ".join(prose_fields))
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2400)

    def test_micro_locations_and_checklist_are_complete(self) -> None:
        self.assertEqual(4, len(self.spec.micro_locations))
        for location in self.spec.micro_locations:
            self.assertTrue(location["name"].strip())
            for field in ("best_for", "daily_life", "diligence"):
                self.assertTrue(location[field].strip())
        self.assertEqual(8, len(self.spec.checklist))

    def test_score_audit_uses_the_model_derived_total(self) -> None:
        destinations = json.loads((Path(__file__).parents[1] / "data" / "destinations.json").read_text())
        fukuoka = next(row for row in destinations if row["id"] == "fukuoka-itoshima")
        from src.build_unified_app import consolidate_destination

        enriched = consolidate_destination(fukuoka)
        self.assertEqual(4.27, enriched["decision_score"])
        self.assertEqual(10, len(enriched["decision_dimensions"]))


class PremiumDossierListingTests(unittest.TestCase):
    def test_fukuoka_has_three_to_five_complete_listing_observations(self) -> None:
        listings = json.loads((Path(__file__).parents[1] / "data" / "listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == "fukuoka-itoshima"]
        self.assertGreaterEqual(len(rows), 3)
        self.assertLessEqual(len(rows), 5)
        required = {
            "property_type",
            "listing_name",
            "local_currency",
            "local_price",
            "usd_price",
            "size_m2",
            "usd_per_m2",
            "fx_basis",
            "source_name",
            "source_url",
            "captured_date",
            "confidence",
            "note",
        }
        for row in rows:
            self.assertFalse(required - row.keys())
            self.assertTrue(all(row[field] not in (None, "") for field in required))
            self.assertEqual("JPY", row["local_currency"])
            self.assertEqual("2026-08-21", row["captured_date"])

        self.assertGreaterEqual(len({row["property_type"] for row in rows}), 2)
        notes = " ".join(row["note"].lower() for row in rows)
        self.assertRegex(notes, r"daily-life|practical")
        self.assertRegex(notes, r"coastal|lifestyle|high-end")


class PremiumDossierRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        root = Path(__file__).parents[1]
        destinations = json.loads((root / "data" / "destinations.json").read_text())
        listings = json.loads((root / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        fukuoka = next(row for row in enriched if row["id"] == "fukuoka-itoshima")
        valencia = next(row for row in enriched if row["id"] == "valencia")
        cls.fukuoka_html = build_destination_page(fukuoka, listings, enriched, [])
        cls.valencia_html = build_destination_page(valencia, listings, enriched, [])

    def test_fukuoka_uses_the_premium_renderer_in_specification_order(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.fukuoka_html)
        section_ids = ["verdict", "lenses", "scores", "listings", "locations", "checklist", "sources"]
        positions = [self.fukuoka_html.index(f'id="{section_id}"') for section_id in section_ids]
        self.assertEqual(sorted(positions), positions)
        for lens in get_premium_dossier("fukuoka-itoshima").lenses:
            self.assertEqual(1, self.fukuoka_html.count(lens.heading))

    def test_score_and_listing_tables_are_model_and_data_derived(self) -> None:
        self.assertEqual(10, self.fukuoka_html.count('class="premium-score-row"'))
        self.assertIn("4.3/5", self.fukuoka_html)
        self.assertEqual(3, self.fukuoka_html.count('class="premium-listing-row"'))
        self.assertIn("31,800,000 JPY", self.fukuoka_html)
        self.assertIn("2026-08-21", self.fukuoka_html)

    def test_page_has_authorship_schema_links_and_final_references(self) -> None:
        self.assertIn("Global Home Atlas Research Team", self.fukuoka_html)
        self.assertIn('"@type":"Article"', self.fukuoka_html)
        self.assertIn('"@type":"BreadcrumbList"', self.fukuoka_html)
        self.assertIn('/japan-retirement-property-foreign-buyers/', self.fukuoka_html)
        self.assertIn('/methodology/', self.fukuoka_html)
        self.assertNotIn("25-destination", self.fukuoka_html)
        article_end = self.fukuoka_html.index("</article>")
        self.assertLess(self.fukuoka_html.index('id="sources"'), article_end)
        self.assertNotIn("<section", self.fukuoka_html[self.fukuoka_html.index('id="sources"'):article_end])

    def test_other_destinations_keep_the_generic_renderer(self) -> None:
        self.assertNotIn('<body class="premium-dossier">', self.valencia_html)
        self.assertNotIn('id="lenses"', self.valencia_html)

    def test_three_images_are_distributed_once_with_accessible_text(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertEqual(3, self.fukuoka_html.count("<figure"))
        self.assertNotIn("montage", self.fukuoka_html.lower())
        for image in spec.images:
            self.assertEqual(1, self.fukuoka_html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.fukuoka_html)
            asset = Path(__file__).parents[1] / "src" / "site_assets" / Path(image.src).name
            self.assertTrue(asset.exists())

    def test_premium_css_has_mobile_readability_and_contained_tables(self) -> None:
        self.assertIn("@media (max-width: 560px)", self.fukuoka_html)
        self.assertIn(".premium-section p, .premium-section li { font-size: 16px; }", self.fukuoka_html)
        self.assertIn("overflow-x: auto", self.fukuoka_html)
        self.assertIn("font-weight: 500", self.fukuoka_html)


class PremiumDossierPublishingRuleTests(unittest.TestCase):
    def test_japan_guide_links_its_first_substantive_fukuoka_mention(self) -> None:
        from src import build_unified_app

        destinations = [
            build_unified_app.consolidate_destination(row)
            for row in build_unified_app.load_json("destinations.json")
        ]
        page = next(
            row for row in build_unified_app.SEO_PAGES
            if row["slug"] == "japan-retirement-property-foreign-buyers"
        )
        html = build_unified_app.build_seo_page(page, destinations, build_unified_app.SEO_PAGES)
        self.assertIn(
            '<a class="editorial-destination-link" href="/destinations/fukuoka-itoshima/">Fukuoka and Itoshima</a>',
            html,
        )

    def test_publish_checklist_contains_the_premium_dossier_gate(self) -> None:
        checklist = (Path(__file__).parents[1] / "docs" / "CONTENT_PUBLISH_READINESS_CHECKLIST.md").read_text()
        checklist = checklist.lower()
        self.assertIn("five editorial lenses", checklist)
        self.assertIn("three to five representative listing observations", checklist)
        self.assertIn("exactly one 10-row score table", checklist)


if __name__ == "__main__":
    unittest.main()
