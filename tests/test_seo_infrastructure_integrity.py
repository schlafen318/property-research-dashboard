from __future__ import annotations

import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from src import build_unified_app
from src.premium_destination_dossiers import PREMIUM_DESTINATION_DOSSIERS


ROOT = Path(__file__).parents[1]
ARTIFACTS = ROOT / "artifacts"


def artifact_for_url(url: str) -> Path:
    relative = url.removeprefix("https://globalhomeatlas.com/").rstrip("/")
    return ARTIFACTS / relative / "index.html" if relative else ARTIFACTS / "index.html"


class SeoInfrastructureIntegrityTests(unittest.TestCase):
    def test_every_sitemap_url_has_a_deployable_artifact(self) -> None:
        root = ET.parse(ARTIFACTS / "sitemap.xml").getroot()
        urls = [
            node.text
            for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if node.text
        ]

        missing = [url for url in urls if not artifact_for_url(url).is_file()]

        self.assertEqual([], missing)

    def test_every_registered_premium_dossier_has_premium_generated_html(self) -> None:
        stale = []
        for destination_id in PREMIUM_DESTINATION_DOSSIERS:
            path = ARTIFACTS / "destinations" / destination_id / "index.html"
            if not path.is_file() or '<body class="premium-dossier">' not in path.read_text():
                stale.append(destination_id)

        self.assertEqual([], stale)

    def test_tracking_verifier_accepts_the_current_public_funnel(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_premium_dossier_handoff_links_comparable_destinations_compactly(self) -> None:
        destinations = [
            build_unified_app.consolidate_destination(item)
            for item in build_unified_app.load_json("destinations.json")
        ]
        listings = build_unified_app.load_json("listings.json")
        destination = next(item for item in destinations if item["id"] == "fukuoka-itoshima")

        html = build_unified_app.build_destination_page(
            destination,
            listings,
            destinations,
            build_unified_app.SEO_PAGES,
        )

        self.assertIn(
            '<a href="/destinations/hakone-izu/">Hakone / Izu</a>',
            html,
        )
        self.assertIn(
            '<a href="/destinations/hakuba/">Hakuba</a>',
            html,
        )
        self.assertNotIn("Related destinations", html)

        lake_tahoe = next(item for item in destinations if item["id"] == "lake-tahoe")
        lake_tahoe_html = build_unified_app.build_destination_page(
            lake_tahoe,
            listings,
            destinations,
            build_unified_app.SEO_PAGES,
        )
        self.assertIn(
            '<a href="/destinations/park-city-deer-valley/">Park City / Deer Valley</a>',
            lake_tahoe_html,
        )
        self.assertIn(
            '<a href="/destinations/miami-fort-lauderdale/">Miami / Fort Lauderdale</a>',
            lake_tahoe_html,
        )
        self.assertNotIn('/destinations/los-angeles-orange-county/', lake_tahoe_html)

        bali = next(item for item in destinations if item["id"] == "bali")
        bali_html = build_unified_app.build_destination_page(
            bali,
            listings,
            destinations,
            build_unified_app.SEO_PAGES,
        )
        self.assertIn(
            '<a href="/destinations/fukuoka-itoshima/">Fukuoka / Itoshima</a>',
            bali_html,
        )

        dubai = next(item for item in destinations if item["id"] == "dubai")
        dubai_html = build_unified_app.build_destination_page(
            dubai,
            listings,
            destinations,
            build_unified_app.SEO_PAGES,
        )
        self.assertIn('<a href="/destinations/bali/">Bali</a>', dubai_html)
        self.assertIn(
            '<a href="/destinations/phuket-koh-samui/">Phuket / Koh Samui</a>',
            dubai_html,
        )
        self.assertIn(
            '<a href="/destinations/fukuoka-itoshima/">Fukuoka / Itoshima</a>',
            dubai_html,
        )


if __name__ == "__main__":
    unittest.main()
