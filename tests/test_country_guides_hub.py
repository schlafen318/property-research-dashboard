from __future__ import annotations

import json
import re
import unittest

from src import build_unified_app


class CountryGuidesHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = [
            build_unified_app.consolidate_destination(item)
            for item in build_unified_app.load_json("destinations.json")
        ]

    def render(self) -> str:
        return build_unified_app.build_country_guides_hub_page(self.destinations)

    def test_renders_each_country_once_with_acquisition_and_destination_links(self) -> None:
        html = self.render()
        for hub in build_unified_app.COUNTRY_HUBS:
            self.assertEqual(1, html.count(f'data-country="{hub["slug"]}"'))
            self.assertIn(f'href="/countries/{hub["slug"]}/"', html)
            for destination_id in hub["destination_ids"]:
                destination = next(item for item in self.destinations if item["id"] == destination_id)
                self.assertIn(
                    f'href="/destinations/{build_unified_app.destination_slug(destination)}/"',
                    html,
                )

    def test_retirement_links_appear_only_for_published_guides(self) -> None:
        html = self.render()
        published = {
            slug
            for hub in build_unified_app.COUNTRY_HUBS
            for slug in hub.get("guide_slugs", [])
            if slug.endswith("retirement-property-foreign-buyers")
        }
        for slug in published:
            self.assertIn(f'href="/{slug}/"', html)
        self.assertEqual(len(published), html.count('data-track="country_retirement_guide_click"'))
        self.assertNotIn("coming soon", html.lower())

    def test_has_search_metadata_breadcrumbs_and_collection_schema(self) -> None:
        html = self.render()
        self.assertIn("<title>Country Property Guides for Foreign Buyers | Global Home Atlas</title>", html)
        self.assertIn('<link rel="canonical" href="https://globalhomeatlas.com/countries/">', html)
        self.assertIn('aria-label="Breadcrumb"', html)
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        payloads = [json.loads(script) for script in scripts]
        entities = [entity for payload in payloads for entity in (payload if isinstance(payload, list) else [payload])]
        types = {entity.get("@type") for entity in entities}
        self.assertIn("CollectionPage", types)
        self.assertIn("ItemList", types)
        self.assertIn("BreadcrumbList", types)

    def test_filter_is_accessible_and_progressive(self) -> None:
        html = self.render()
        self.assertIn('id="country-filter"', html)
        self.assertIn('aria-controls="country-directory"', html)
        self.assertIn('id="country-filter-status"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('data-track="country_filter_use"', html)

    def test_directory_links_use_regular_editorial_weight(self) -> None:
        html = self.render()
        self.assertIn(".country-directory__row nav a { width: fit-content; font-weight: 400;", html)
        self.assertNotIn(".country-directory__row nav a { width: fit-content; font-weight: 650;", html)

    def test_navigation_and_sitemap_entries_include_the_hub(self) -> None:
        self.assertIn('href="/countries/">Country Guides</a>', build_unified_app.primary_nav_links_html())
        self.assertIn(
            (build_unified_app.page_url("countries"), "0.90"),
            build_unified_app.sitemap_url_entries(self.destinations),
        )


if __name__ == "__main__":
    unittest.main()
