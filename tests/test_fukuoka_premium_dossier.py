import unittest
import json
import re
from pathlib import Path

from PIL import Image

from src.premium_destination_dossiers import (
    DECISION_DIMENSION_KEYS,
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


ROOT = Path(__file__).parents[1]


class PremiumDossierContractTests(unittest.TestCase):
    def test_only_reviewed_prototypes_use_the_premium_registry(self) -> None:
        self.assertTrue({"fukuoka-itoshima", "valencia", "algarve-cascais", "madeira", "malaga-costa-del-sol", "lake-como", "hakone-izu", "hakuba", "costa-brava-girona", "park-city-deer-valley", "crete", "niseko", "annecy", "mallorca", "croatia-istria-dalmatia", "queenstown", "phuket-koh-samui"}.issubset(set(PREMIUM_DESTINATION_DOSSIERS)))
        self.assertIsNotNone(get_premium_dossier("fukuoka-itoshima"))
        self.assertIsNotNone(get_premium_dossier("valencia"))

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
        self.assertEqual(3, len(spec.market_anchors))
        self.assertEqual("sources", spec.nav_items[-1][0])

    def test_fukuoka_declares_property_anchor_associations_and_image_roles(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertEqual((0, 1, 2), spec.property_anchor_indexes)
        self.assertEqual(
            ["defining-place", "built-environment-access", "decision-texture"],
            [image.role for image in spec.images],
        )

    def test_fukuoka_images_are_distinct_and_auditable(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertEqual(3, len({image.src for image in spec.images}))

        provenance = (
            ROOT / "docs" / "research" / "fukuoka-itoshima-image-provenance.md"
        ).read_text()
        for dossier_image in spec.images:
            filename = Path(dossier_image.src).name
            with self.subTest(filename=filename):
                self.assertIn(filename, provenance)
                with Image.open(ROOT / "src" / "site_assets" / filename) as image:
                    self.assertGreaterEqual(image.width, 900)
                    self.assertGreaterEqual(image.height, 600)
                    self.assertIn(f"{image.width} × {image.height}", provenance)

        self.assertIn("No repeated older-people-walking motif", provenance)


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

    def test_reader_copy_contains_conclusions_not_production_commentary(self) -> None:
        reader_copy = " ".join((
            self.spec.lenses_intro,
            self.spec.assessment_intro,
            self.spec.listings_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
        )).lower()
        for phrase in (
            "recorded dataset",
            "the prose below explains",
            "appears once",
            "the listings below",
            "public-market check on the asking listings",
            "representative property evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, reader_copy)
        self.assertIn("¥31.8 million", self.spec.listings_intro)
        self.assertIn("¥180 million", self.spec.listings_intro)
        self.assertIn("rail", self.spec.listings_intro.lower())
        self.assertIn("resale", self.spec.listings_intro.lower())

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

    def test_hero_lede_is_concise_enough_to_reveal_the_story_on_mobile(self) -> None:
        self.assertLessEqual(len(self.spec.lede.split()), 85)
        self.assertIn("city-and-coast", self.spec.lede)

    def test_market_anchors_use_official_land_evidence_and_clear_limits(self) -> None:
        self.assertEqual(3, len(self.spec.market_anchors))
        anchors = " ".join(
            " ".join(str(value) for value in anchor.values())
            for anchor in self.spec.market_anchors
        )
        self.assertIn("reinfolib.mlit.go.jp", anchors)
        self.assertIn("pref.fukuoka.lg.jp", anchors)
        self.assertRegex(anchors.lower(), r"land|finished-home")
        for anchor in self.spec.market_anchors:
            with self.subTest(anchor=anchor["location"]):
                self.assertTrue(anchor["location"].strip())
                self.assertTrue(anchor["evidence"].strip())
                self.assertTrue(anchor["buyer_read"].strip())
                self.assertTrue(anchor["source_url"].startswith("https://"))

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

    def test_score_reads_are_complete_concise_and_destination_specific(self) -> None:
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        score_reads = getattr(self.spec, "score_reads", {})
        self.assertEqual(DECISION_DIMENSION_KEYS, set(score_reads))
        for key, research_read in score_reads.items():
            with self.subTest(key=key):
                words = research_read.split()
                self.assertGreaterEqual(len(words), 12)
                self.assertLessEqual(len(words), 34)
                self.assertRegex(research_read, r"Fukuoka|Itoshima")


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
        from src.build_unified_app import build_destination_page, consolidate_destination, load_content_overrides

        root = Path(__file__).parents[1]
        destinations = json.loads((root / "data" / "destinations.json").read_text())
        listings = json.loads((root / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        fukuoka = next(row for row in enriched if row["id"] == "fukuoka-itoshima")
        valencia = next(row for row in enriched if row["id"] == "valencia")
        cls.fukuoka_html = build_destination_page(fukuoka, listings, enriched, [])
        cls.valencia_html = build_destination_page(valencia, listings, enriched, [])
        cls.fukuoka_html_with_site_overrides = build_destination_page(
            fukuoka,
            listings,
            enriched,
            [],
            content_overrides=load_content_overrides(),
        )

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
        self.assertEqual(3, self.fukuoka_html.count('class="premium-property-record"'))
        self.assertIn("31,800,000 JPY", self.fukuoka_html)
        self.assertIn("2026-08-21", self.fukuoka_html)

    def test_property_evidence_renders_once_with_integrated_local_comparisons(self) -> None:
        self.assertEqual(1, self.fukuoka_html.count('<section class="premium-section" id="listings">'))
        self.assertIn("<h2>What homes cost</h2>", self.fukuoka_html)
        self.assertEqual(3, self.fukuoka_html.count('class="premium-property-record"'))
        self.assertEqual(3, self.fukuoka_html.count('class="premium-local-comparison"'))
        self.assertNotIn("Official market anchors", self.fukuoka_html)
        self.assertNotIn('id="official-market-anchors"', self.fukuoka_html)
        for value in (
            "121,700–132,400 JPY/m²",
            "82,900–108,500 JPY/m²",
            "7,720–41,400 JPY/m²",
        ):
            with self.subTest(value=value):
                self.assertEqual(1, self.fukuoka_html.count(value))
        self.assertIn("reinfolib.mlit.go.jp", self.fukuoka_html)
        self.assertIn("pref.fukuoka.lg.jp", self.fukuoka_html)

    def test_property_records_use_readable_fields_not_a_wide_desktop_table(self) -> None:
        self.assertNotIn('<table class="premium-listing-table', self.fukuoka_html)
        self.assertNotIn("<th>USD comparison</th>", self.fukuoka_html)
        for label in (
            "Asking price", "Area", "USD comparison", "Buyer relevance",
            "Local comparison", "View current listing",
        ):
            with self.subTest(label=label):
                self.assertIn(label, self.fukuoka_html)
        listings_section = self.fukuoka_html.split('id="listings"', 1)[1].split('</section>', 1)[0]
        self.assertNotIn("Captured", listings_section)
        self.assertNotIn("confidence", listings_section.lower())

    def test_score_table_uses_dossier_specific_research_reads(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        score_reads = getattr(spec, "score_reads", {})
        self.assertEqual(10, len(score_reads))
        for research_read in score_reads.values():
            self.assertEqual(1, self.fukuoka_html.count(research_read))
        self.assertNotIn(
            "Natural setting, food culture, and repeatable year-round reasons to be there.",
            self.fukuoka_html,
        )

    def test_score_table_uses_plain_reader_facing_language(self) -> None:
        self.assertIn(
            "Here’s how Fukuoka / Itoshima scores on the ten factors that matter most when choosing a long-term home abroad.",
            self.fukuoka_html,
        )
        self.assertIn("<th>Atlas read</th>", self.fukuoka_html)
        self.assertNotIn("comparative inputs", self.fukuoka_html.lower())
        self.assertNotIn("research judgments", self.fukuoka_html.lower())
        self.assertNotIn("<th>Research read</th>", self.fukuoka_html)
        self.assertNotIn("<th>What it means</th>", self.fukuoka_html)

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

    def test_reviewed_valencia_destination_uses_the_premium_renderer(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.valencia_html)
        self.assertIn('id="lenses"', self.valencia_html)

    def test_unrelated_site_overrides_do_not_disable_premium_renderer(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.fukuoka_html_with_site_overrides)

    def test_three_images_are_distributed_once_with_accessible_text(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertEqual(3, self.fukuoka_html.count('src="/assets/fukuoka-itoshima-'))
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

    def test_where_to_look_has_an_accessible_four_stop_orientation_schematic(self) -> None:
        self.assertIn('class="premium-location-orientation"', self.fukuoka_html)
        self.assertIn("Orientation schematic—not to scale", self.fukuoka_html)
        self.assertEqual(4, self.fukuoka_html.count('class="premium-location-stop"'))
        for location in ("Central Fukuoka", "Meinohama corridor", "Maebaru", "Itoshima coast"):
            self.assertIn(location, self.fukuoka_html)

    def test_score_property_and_location_evidence_are_readable_records(self) -> None:
        self.assertEqual(2, self.fukuoka_html.count('class="premium-table-wrap premium-card-table-wrap"'))
        self.assertEqual(3, self.fukuoka_html.count('class="premium-property-record"'))
        self.assertIn('data-label="Score"', self.fukuoka_html)
        self.assertIn('data-label="Atlas read"', self.fukuoka_html)
        self.assertIn('<dt>Asking price</dt>', self.fukuoka_html)
        self.assertIn('<dt>Buyer relevance</dt>', self.fukuoka_html)
        self.assertIn('data-label="Micro-location"', self.fukuoka_html)
        self.assertIn('data-label="Primary diligence"', self.fukuoka_html)
        self.assertIn(".premium-card-table-wrap { overflow: visible;", self.fukuoka_html)
        self.assertIn(".premium-card-table tbody tr { display: grid;", self.fukuoka_html)


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
        self.assertIn("destination-specific research read", checklist)
        self.assertIn("plain reader-facing language", checklist)
        self.assertIn("orientation schematic", checklist)
        self.assertIn("official market anchors", checklist)
        self.assertIn("stacked labelled records", checklist)

    def test_premium_dossier_rulebook_defines_the_repeatable_quality_standard(self) -> None:
        docs_dir = Path(__file__).parents[1] / "docs"
        checklist = (docs_dir / "CONTENT_PUBLISH_READINESS_CHECKLIST.md").read_text()
        rulebook = (docs_dir / "PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md").read_text().lower()

        self.assertIn("[Premium Destination Dossier Rule Book](PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md)", checklist)
        for required_standard in (
            "definition of an atlas 10/10 dossier",
            "required content contract",
            "the five-lens model",
            "score governance",
            "official market anchors",
            "shared visual system",
            "hard publishing gates",
            "the 100-point quality scorecard",
            "desktop and mobile review script",
            "update policy for future editions",
            "rollout rule for existing destinations",
        ):
            self.assertIn(required_standard, rulebook)
        self.assertIn("95–100, all hard gates pass", rulebook)
        self.assertIn("do not bulk-convert pages", rulebook)


if __name__ == "__main__":
    unittest.main()
