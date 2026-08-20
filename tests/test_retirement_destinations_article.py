from __future__ import annotations

import json
import re
import struct
import subprocess
import unittest
from pathlib import Path

from src.build_unified_app import destination_slug


ROOT = Path(__file__).resolve().parents[1]
SLUG = "retirement-destinations-ranked-by-cost"
PAGE = ROOT / "artifacts" / SLUG / "index.html"
ASSET_NAMES = (
    "retirement-destinations-required-capital.png",
    "retirement-destinations-capital-breakdown.png",
)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    return struct.unpack(">II", signature[16:24])


class RetirementDestinationsArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["python3", "src/build_unified_app.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.compact_html = re.sub(r"\s+", "", cls.html)

    def test_article_has_indexable_metadata_and_structured_data(self) -> None:
        self.assertIn(
            "<title>Retirement Destinations Ranked by Cost (2026) | Global Home Atlas</title>",
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/retirement-destinations-ranked-by-cost/">',
            self.html,
        )
        self.assertIn(
            '<meta name="description" content="Compare all 30 Global Home Atlas retirement destinations by required capital, annual spending, reserves, and optional property costs using one methodology.">',
            self.html,
        )
        self.assertIn(
            "<h1>30 Retirement Destinations Ranked by How Much You Need</h1>",
            self.html,
        )
        self.assertIn('"@type":"Article"', self.compact_html)
        self.assertIn('"@type":"FAQPage"', self.compact_html)
        self.assertIn('"@type":"ItemList"', self.compact_html)
        self.assertIn('"numberOfItems":30', self.compact_html)
        self.assertIn('"@type":"ImageObject"', self.compact_html)

    def test_ranking_shows_top_ten_then_expands_ranks_eleven_to_thirty(self) -> None:
        ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
        visible = ranking.split('<details class="ranking-more">', 1)[0]
        expandable = ranking.split('<details class="ranking-more">', 1)[1]
        self.assertEqual(10, visible.count('class="ranking-row"'))
        self.assertEqual(20, expandable.count('class="ranking-row"'))
        self.assertIn("View 20 more destinations", expandable)
        self.assertIn("</details>", expandable)

    def test_every_destination_is_ranked_once_and_only_top_ten_have_notes(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        retirement_ids = {
            item["destination_id"]
            for item in json.loads((ROOT / "data" / "retirement_costs.json").read_text(encoding="utf-8"))["destinations"]
        }
        ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
        for destination in destinations:
            href = f'href="/destinations/{destination_slug(destination)}/"'
            expected_count = 1 if destination["id"] in retirement_ids else 0
            self.assertEqual(expected_count, ranking.count(href), destination["id"])
        notes = self.html.split('class="destination-notes"', 1)[1].split("</ol>", 1)[0]
        self.assertEqual(10, notes.count("<li>"))

    def test_table_ranks_destinations_by_couple_required_capital(self) -> None:
        marker = 'id="ranking"'
        self.assertIn(marker, self.html)
        table = self.html.split(marker, 1)[1].split("</section>", 1)[0]
        ordered_names = [
            "Fukuoka / Itoshima",
            "Hakone / Izu",
            "Crete",
            "Valencia",
            "Algarve / Cascais",
            "Málaga / Costa del Sol",
            "Madeira",
            "Lake Como",
        ]
        positions = [table.index(name) for name in ordered_names]
        self.assertEqual(sorted(positions), positions)
        for expected_value in ("$1,957,629", "$1,984,243", "$2,634,814"):
            self.assertIn(expected_value, table)
        self.assertIn("Destination", table)
        self.assertIn("Savings needed", table)
        self.assertIn("Home purchase estimate", table)

    def test_methodology_defines_the_cost_rank_without_claiming_lifestyle_rank(self) -> None:
        self.assertIn("couple renting", self.html.lower())
        self.assertIn("30-year retirement horizon", self.html)
        self.assertIn("3.5% withdrawal rate", self.html)
        self.assertIn("12 months of expenses", self.html)
        self.assertIn("no pension or other passive income", self.html.lower())
        self.assertIn("Destinations, not countries", self.html)
        self.assertIn("does not rank lifestyle quality", self.html.lower())
        self.assertIn("Data reviewed 2026-08-18", self.html)

    def test_article_uses_a_single_reading_flow_without_duplicate_metric_panels(self) -> None:
        self.assertIn(
            '<nav class="article-toc" aria-label="In this article">',
            self.html,
        )
        self.assertIn('class="article-callout"', self.html)
        self.assertIn('class="destination-notes"', self.html)
        self.assertNotIn('class="article-summary"', self.html)
        self.assertNotIn('class="article-aside"', self.html)
        self.assertNotIn('class="rank-card"', self.html)
        self.assertNotIn("<dl>", self.html)

    def test_primary_ranking_table_focuses_on_decision_relevant_numbers(self) -> None:
        marker = 'id="ranking"'
        table = self.html.split(marker, 1)[1].split("</table>", 1)[0]
        self.assertIn("Atlas rank", table)
        self.assertIn("Annual cost incl. rent", table)
        self.assertIn("Savings needed", table)
        self.assertIn("Home purchase estimate", table)
        self.assertNotIn("<th>Liquid portfolio</th>", table)
        self.assertNotIn("<th>Emergency reserve</th>", table)

    def test_annual_cost_method_is_explained_next_to_the_ranking(self) -> None:
        ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
        self.assertIn("How annual cost is estimated", ranking)
        self.assertIn("Annual cost includes rent", ranking)
        self.assertIn("private healthcare", ranking)
        self.assertIn("travel", ranking)
        self.assertIn("contingency", ranking)
        self.assertIn("Home purchase costs are separate", ranking)

    def test_ranking_headers_are_sortable_and_use_plain_language(self) -> None:
        ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
        for key, label in (
            ("rank", "Cost rank"),
            ("atlas", "Atlas rank"),
            ("name", "Destination"),
            ("annual", "Annual cost incl. rent"),
            ("savings", "Savings needed"),
            ("property", "Home purchase estimate"),
        ):
            self.assertIn(f'data-sort-key="{key}"', ranking)
            self.assertIn(f'>{label}<', ranking)
        self.assertNotIn("Required retirement capital", ranking)
        self.assertNotIn("Property capital", ranking)

    def test_hero_actions_are_separate_and_redundant_eyebrow_is_removed(self) -> None:
        hero = self.html.split('<header class="page-hero">', 1)[1].split("</header>", 1)[0]
        self.assertNotIn('class="page-eyebrow"', hero)
        self.assertIn('class="page-button"', hero)
        self.assertIn('class="page-button page-button-secondary"', hero)
        self.assertIn("Calculate your plan", hero)
        self.assertIn("View rankings", hero)

    def test_sources_are_available_in_a_low_prominence_disclosure(self) -> None:
        methodology = self.html.split('id="methodology"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("<h3>Cost evidence</h3>", methodology)
        self.assertIn('<details class="source-more">', methodology)
        self.assertIn("<summary>Sources and data notes</summary>", methodology)
        sources = methodology.split('<details class="source-more">', 1)[1].split("</details>", 1)[0]
        self.assertEqual(30, sources.count("<li>"))

    def test_two_accessible_infographics_have_downloadable_pngs(self) -> None:
        for asset_name in ASSET_NAMES:
            with self.subTest(asset_name=asset_name):
                source = ROOT / "src" / "site_assets" / asset_name
                public = ROOT / "artifacts" / "assets" / asset_name
                self.assertTrue(source.exists())
                self.assertTrue(public.exists())
                self.assertEqual((1600, 900), png_dimensions(source))
                self.assertGreater(source.stat().st_size, 20_000)
                self.assertIn(f'src="/assets/{asset_name}"', self.html)
                self.assertIn(f'href="/assets/{asset_name}" download', self.html)
        self.assertIn(
            'alt="Lowest-cost 10 of 30 retirement destinations ranked by required capital for a couple renting"',
            self.html,
        )
        self.assertIn(
            'alt="Capital breakdown for the lowest-cost 10 of 30 retirement destinations"',
            self.html,
        )
        self.assertIn("lowest-cost 10 of 30", self.html.lower())

    def test_article_is_connected_to_the_retirement_content_cluster(self) -> None:
        for href in (
            "/retirement-abroad-calculator/",
            "/methodology/",
            "/destinations/fukuoka-itoshima/",
            "/destinations/valencia/",
            "/best-places-to-buy-property-abroad-for-retirement/",
        ):
            with self.subTest(href=href):
                self.assertIn(f'href="{href}"', self.html)

        guides = (ROOT / "artifacts" / "guides" / "index.html").read_text(encoding="utf-8")
        calculator = (ROOT / "artifacts" / "retirement-abroad-calculator" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'href="/{SLUG}/"', guides)
        self.assertIn(f'href="/{SLUG}/"', calculator)

    def test_homepage_links_to_ranked_retirement_article_once(self) -> None:
        homepage = (ROOT / "artifacts" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'href="/{SLUG}/"', homepage)
        self.assertEqual(1, homepage.count(f'href="/{SLUG}/"'))

    def test_sitemap_contains_one_article_url(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            sitemap.count(
                "https://globalhomeatlas.com/retirement-destinations-ranked-by-cost/"
            ),
        )


if __name__ == "__main__":
    unittest.main()
