from __future__ import annotations

import json
from pathlib import Path
import unittest

from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]


def rendered_inputs() -> tuple[list[dict], list[dict]]:
    destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
    listings = json.loads((ROOT / "data" / "listings.json").read_text())
    return [build_unified_app.consolidate_destination(item) for item in destinations], listings


class CountryContentLinkGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations, cls.listings = rendered_inputs()
        cls.destinations_by_id = {item["id"]: item for item in cls.destinations}

    def test_retirement_guides_link_to_acquisition_guide_and_all_country_dossiers(self) -> None:
        for hub in build_unified_app.COUNTRY_HUBS:
            retirement_slug = build_unified_app.country_retirement_guide_slug(hub)
            if not retirement_slug:
                continue
            page = next(
                item for item in build_unified_app.SEO_PAGES if item["slug"] == retirement_slug
            )
            html = build_unified_app.build_seo_page(
                page, self.destinations, build_unified_app.SEO_PAGES
            )
            with self.subTest(country=hub["country"], link="acquisition"):
                self.assertIn(f'href="/countries/{hub["slug"]}/"', html)
            for destination_id in hub.get("destination_ids", []):
                destination = self.destinations_by_id[destination_id]
                destination_slug = build_unified_app.destination_slug(destination)
                with self.subTest(country=hub["country"], destination=destination_slug):
                    self.assertIn(f'href="/destinations/{destination_slug}/"', html)

    def test_country_dossiers_link_to_both_national_guide_types(self) -> None:
        for hub in build_unified_app.COUNTRY_HUBS:
            retirement_slug = build_unified_app.country_retirement_guide_slug(hub)
            if not retirement_slug:
                continue
            for destination_id in hub.get("destination_ids", []):
                destination = self.destinations_by_id[destination_id]
                html = build_unified_app.build_destination_page(
                    destination,
                    self.listings,
                    self.destinations,
                    build_unified_app.SEO_PAGES,
                )
                with self.subTest(country=hub["country"], destination=destination_id):
                    self.assertIn(f'href="/countries/{hub["slug"]}/"', html)
                    self.assertIn(f'href="/{retirement_slug}/"', html)


if __name__ == "__main__":
    unittest.main()
