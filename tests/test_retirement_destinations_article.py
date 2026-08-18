from __future__ import annotations

import re
import struct
import subprocess
import unittest
from pathlib import Path


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
            '<meta name="description" content="Compare eight retirement destinations by required capital, annual spending, portfolio needs, reserves, and optional property costs using one methodology.">',
            self.html,
        )
        self.assertIn(
            "<h1>8 Retirement Destinations Ranked by How Much You Need</h1>",
            self.html,
        )
        self.assertIn('"@type":"Article"', self.compact_html)
        self.assertIn('"@type":"FAQPage"', self.compact_html)
        self.assertIn('"@type":"ImageObject"', self.compact_html)

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
        self.assertIn("Country", table)
        self.assertIn("Required retirement capital", table)
        self.assertIn("Property capital", table)

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
        self.assertIn("Annual spending", table)
        self.assertIn("Required retirement capital", table)
        self.assertIn("Property capital", table)
        self.assertNotIn("<th>Liquid portfolio</th>", table)
        self.assertNotIn("<th>Emergency reserve</th>", table)

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
            'alt="Eight retirement destinations ranked from lowest to highest required capital for a couple renting"',
            self.html,
        )
        self.assertIn(
            'alt="Annual spending, liquid portfolio, emergency reserve, and optional property capital across eight retirement destinations"',
            self.html,
        )

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
