from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import re
import unittest
from urllib.parse import urlsplit

from src import build_unified_app
from src.foreign_buyer_country_guides import (
    FOREIGN_BUYER_COUNTRY_GUIDES,
    get_foreign_buyer_country_guide,
    validate_foreign_buyer_country_guide,
)


def render_country(slug: str) -> str:
    hub = next(item for item in build_unified_app.COUNTRY_HUBS if item["slug"] == slug)
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_country_hub_page(
        hub, destinations, build_unified_app.SEO_PAGES
    )


def valid_guide_fixture() -> dict:
    sourced = {"heading": "Heading", "body": "Body", "source_urls": ["https://example.gov/source"]}
    return {
        "country": "Japan",
        "title": "Title",
        "description": "Description",
        "h1": "H1",
        "summary": "Summary",
        "date_published": "2026-08-27",
        "date_reviewed": "2026-08-27",
        "hero_image": {"src": "/assets/example.webp", "alt": "Alt", "caption": "Caption"},
        "direct_answers": {
            key: {"answer": "Answer", "source_urls": ["https://example.gov/source"]}
            for key in ("ownership", "residency", "financing", "short_rentals")
        },
        "eligibility_sections": [deepcopy(sourced)],
        "purchase_steps": [
            {"heading": f"Step {index}", "body": "Body", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 6)
        ],
        "cost_rows": [
            {"cost": label, "when": "When", "buyer_read": "Read", "source_urls": ["https://example.gov/source"]}
            for label in (
                "Purchase price",
                "Acquisition and registration taxes",
                "Annual ownership costs",
                "Eventual sale and transfer-out costs",
            )
        ],
        "ownership_rules": [
            {"heading": label, "body": "Body", "source_urls": ["https://example.gov/source"]}
            for label in (
                "Owner records",
                "Condominium repairs",
                "Short-rental authority",
                "Tax and hazard files",
            )
        ],
        "destination_reads": {
            destination_id: {"best_for": "Best", "verify_first": "Verify"}
            for destination_id in ("fukuoka-itoshima", "hakone-izu", "hakuba", "niseko")
        },
        "buyer_checklist": ["Check"],
        "faqs": [
            {"question": f"Question {index}", "answer": "Answer", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 4)
        ],
        "primary_sources": [{"label": "Source", "url": "https://example.gov/source"}],
        "retirement_guide_slug": "japan-retirement-property-foreign-buyers",
    }


class ForeignBuyerCountryGuideContractTests(unittest.TestCase):
    destination_ids = ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"]

    def test_only_japan_is_migrated_for_the_pilot(self) -> None:
        self.assertEqual(["japan-property"], sorted(FOREIGN_BUYER_COUNTRY_GUIDES))
        self.assertIsNotNone(get_foreign_buyer_country_guide("japan-property"))
        self.assertIsNone(get_foreign_buyer_country_guide("spain-property"))

    def test_validator_rejects_missing_required_content(self) -> None:
        guide = valid_guide_fixture()
        guide.pop("purchase_steps")

        with self.assertRaisesRegex(ValueError, "^japan-property: missing purchase_steps$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_requires_four_named_direct_answers(self) -> None:
        guide = valid_guide_fixture()
        guide["direct_answers"].pop("financing")

        with self.assertRaisesRegex(ValueError, "^japan-property: direct_answers missing financing$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_requires_one_read_for_every_destination(self) -> None:
        guide = valid_guide_fixture()
        guide["destination_reads"].pop("niseko")

        with self.assertRaisesRegex(ValueError, "^japan-property: destination_reads missing niseko$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_fewer_than_five_purchase_steps(self) -> None:
        guide = valid_guide_fixture()
        guide["purchase_steps"] = guide["purchase_steps"][:4]

        with self.assertRaisesRegex(ValueError, "^japan-property: purchase_steps requires at least five steps$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_fewer_than_four_cost_rows(self) -> None:
        guide = valid_guide_fixture()
        guide["cost_rows"] = guide["cost_rows"][:3]

        with self.assertRaisesRegex(ValueError, "^japan-property: cost_rows requires at least four rows$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_fewer_than_three_faqs(self) -> None:
        guide = valid_guide_fixture()
        guide["faqs"] = guide["faqs"][:2]

        with self.assertRaisesRegex(ValueError, "^japan-property: faqs requires at least three questions$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_empty_primary_sources(self) -> None:
        guide = valid_guide_fixture()
        guide["primary_sources"] = []

        with self.assertRaisesRegex(ValueError, "^japan-property: primary_sources is required$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_extra_destination_read(self) -> None:
        guide = valid_guide_fixture()
        guide["destination_reads"]["tokyo"] = {"best_for": "Best", "verify_first": "Verify"}

        with self.assertRaisesRegex(ValueError, "^japan-property: destination_reads must match destination_ids$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_missing_published_date(self) -> None:
        guide = valid_guide_fixture()
        guide.pop("date_published")

        with self.assertRaisesRegex(ValueError, "^japan-property: missing date_published$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_missing_reviewed_date(self) -> None:
        guide = valid_guide_fixture()
        guide.pop("date_reviewed")

        with self.assertRaisesRegex(ValueError, "^japan-property: missing date_reviewed$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_empty_eligibility_sections(self) -> None:
        guide = valid_guide_fixture()
        guide["eligibility_sections"] = []

        with self.assertRaisesRegex(ValueError, "^japan-property: eligibility_sections requires at least one item$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_empty_ownership_rules(self) -> None:
        guide = valid_guide_fixture()
        guide["ownership_rules"] = []

        with self.assertRaisesRegex(ValueError, "^japan-property: ownership_rules requires at least one item$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_empty_buyer_checklist(self) -> None:
        guide = valid_guide_fixture()
        guide["buyer_checklist"] = []

        with self.assertRaisesRegex(ValueError, "^japan-property: buyer_checklist requires at least one item$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_unsourced_legal_item(self) -> None:
        guide = valid_guide_fixture()
        guide["eligibility_sections"][0]["source_urls"] = []

        with self.assertRaisesRegex(ValueError, "^japan-property: eligibility_sections\[0\] requires source_urls$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_extra_direct_answer(self) -> None:
        guide = valid_guide_fixture()
        guide["direct_answers"]["tax"] = {"answer": "Answer", "source_urls": ["https://example.gov/source"]}

        with self.assertRaisesRegex(ValueError, "^japan-property: direct_answers must match required keys$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_blank_published_date(self) -> None:
        guide = valid_guide_fixture()
        guide["date_published"] = ""

        with self.assertRaisesRegex(ValueError, "^japan-property: date_published must be a valid ISO date$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_invalid_reviewed_date(self) -> None:
        guide = valid_guide_fixture()
        guide["date_reviewed"] = "27-08-2026"

        with self.assertRaisesRegex(ValueError, "^japan-property: date_reviewed must be a valid ISO date$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_blank_retirement_guide_slug(self) -> None:
        guide = valid_guide_fixture()
        guide["retirement_guide_slug"] = "  "

        with self.assertRaisesRegex(ValueError, "^japan-property: retirement_guide_slug is required$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_cost_rows_without_acquisition_coverage(self) -> None:
        guide = valid_guide_fixture()
        guide["cost_rows"][1]["cost"] = "Brokerage and professional work"

        with self.assertRaisesRegex(ValueError, "^japan-property: cost_rows missing acquisition coverage$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_cost_rows_without_recurring_coverage(self) -> None:
        guide = valid_guide_fixture()
        guide["cost_rows"][2]["cost"] = "Brokerage and professional work"

        with self.assertRaisesRegex(ValueError, "^japan-property: cost_rows missing recurring ownership coverage$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)

    def test_validator_rejects_ownership_rules_without_tax_obligation(self) -> None:
        guide = valid_guide_fixture()
        guide["ownership_rules"] = [
            {"heading": "Owner records", "body": "Keep records current", "source_urls": ["https://example.gov/source"]},
            {"heading": "Condominium repairs", "body": "Fund repairs", "source_urls": ["https://example.gov/source"]},
            {"heading": "Short rentals", "body": "Recheck lodging authority", "source_urls": ["https://example.gov/source"]},
        ]

        with self.assertRaisesRegex(ValueError, "^japan-property: ownership_rules missing tax and hazard coverage$"):
            validate_foreign_buyer_country_guide("japan-property", guide, self.destination_ids)


class JapanForeignBuyerContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guide = FOREIGN_BUYER_COUNTRY_GUIDES["japan-property"]

    def test_direct_answers_are_short_and_decisive(self) -> None:
        self.assertIn("direct_answers", self.guide)
        self.assertIn(
            "generally buy and register",
            self.guide["direct_answers"]["ownership"]["answer"],
        )
        self.assertIn(
            "does not create",
            self.guide["direct_answers"]["residency"]["answer"],
        )
        self.assertIn(
            "lender-specific",
            self.guide["direct_answers"]["financing"]["answer"],
        )
        self.assertIn(
            "180 days",
            self.guide["direct_answers"]["short_rentals"]["answer"],
        )

    def test_purchase_sequence_covers_offer_through_registration(self) -> None:
        self.assertIn("purchase_steps", self.guide)
        headings = [step["heading"] for step in self.guide["purchase_steps"]]
        self.assertEqual(
            [
                "Confirm the buyer and intended use",
                "Appoint independent advisers",
                "Check the property before offering",
                "Review the contract and Important Matters Explanation",
                "Settle and register the transfer",
                "Complete non-resident reporting and owner administration",
            ],
            headings,
        )

    def test_copy_avoids_generic_process_language(self) -> None:
        rendered_data = repr(self.guide).lower()
        for phrase in (
            "this guide helps",
            "use this page",
            "country thesis",
            "buyer fit",
            "research read",
            "research inputs",
            "same ten-dimension model",
        ):
            self.assertNotIn(phrase, rendered_data)

    def test_residency_claim_cites_official_ownership_status_statement(self) -> None:
        source_url = (
            "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/"
            "english-faq.pdf"
        )
        self.assertIn(
            source_url,
            self.guide["direct_answers"]["residency"]["source_urls"],
        )
        residency_faq = next(
            faq
            for faq in self.guide["faqs"]
            if faq["question"] == "Does buying a home qualify me to live in Japan?"
        )
        self.assertIn(source_url, residency_faq["source_urls"])

    def test_owner_update_rule_cites_current_accessible_moj_guidance(self) -> None:
        current_url = "https://www.moj.go.jp/MINJI/minji05_00693.html"
        old_url = "https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html"
        owner_rule = next(
            rule
            for rule in self.guide["ownership_rules"]
            if rule["heading"] == "Keep the owner record current"
        )
        self.assertIn(current_url, owner_rule["source_urls"])
        self.assertNotIn(old_url, owner_rule["source_urls"])


class JapanForeignBuyerSourceIntegrityTests(unittest.TestCase):
    approved_domains = {
        "mof.go.jp",
        "moj.go.jp",
        "mlit.go.jp",
        "nta.go.jp",
        "gsi.go.jp",
        "mofa.go.jp",
        "city.fukuoka.lg.jp",
    }

    def setUp(self) -> None:
        self.guide = FOREIGN_BUYER_COUNTRY_GUIDES["japan-property"]

    def referenced_source_urls(self) -> list[str]:
        sourced_items = list(self.guide["direct_answers"].values())
        for section_name in (
            "eligibility_sections",
            "purchase_steps",
            "cost_rows",
            "ownership_rules",
            "faqs",
        ):
            sourced_items.extend(self.guide[section_name])
        return [
            url
            for item in sourced_items
            for url in item.get("source_urls", [])
        ]

    def test_referenced_urls_appear_once_in_primary_sources(self) -> None:
        self.assertIn("primary_sources", self.guide)
        self.assertIn("direct_answers", self.guide)
        primary_urls = [source["url"] for source in self.guide["primary_sources"]]
        counts = Counter(primary_urls)

        self.assertEqual(len(primary_urls), len(counts), "primary source URLs must be unique")
        for url in self.referenced_source_urls():
            self.assertEqual(1, counts[url], url)

    def test_primary_sources_use_https_and_approved_official_domains(self) -> None:
        self.assertIn("primary_sources", self.guide)
        for source in self.guide["primary_sources"]:
            parsed = urlsplit(source["url"])
            self.assertEqual("https", parsed.scheme, source["url"])
            self.assertTrue(
                any(
                    parsed.hostname == domain or parsed.hostname.endswith(f".{domain}")
                    for domain in self.approved_domains
                ),
                source["url"],
            )


class ForeignBuyerCountryGuideRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.japan = render_country("japan-property")
        cls.spain = render_country("spain-property")

    def test_japan_uses_the_acquisition_renderer_only(self) -> None:
        self.assertIn('<body class="foreign-buyer-country-guide">', self.japan)
        self.assertNotIn('<body class="foreign-buyer-country-guide">', self.spain)
        self.assertIn("Spain Property Guide for Foreign Buyers", self.spain)

    def test_japan_sections_follow_the_approved_order(self) -> None:
        section_ids = [
            "ownership-answer",
            "purchase-process",
            "costs-financing",
            "after-purchase",
            "destinations",
            "buyer-checklist",
            "faq",
            "sources",
        ]
        positions = [self.japan.index(f'id="{section_id}"') for section_id in section_ids]
        self.assertEqual(positions, sorted(positions))

    def test_core_article_uses_open_sections(self) -> None:
        article = self.japan.split('<article class="foreign-buyer-article">', 1)[1].split(
            "</article>", 1
        )[0]
        self.assertNotIn("<details", article)
        self.assertNotIn("<summary", article)

    def test_japan_excludes_legacy_conversion_content(self) -> None:
        for forbidden in (
            "Country Thesis",
            "Buyer Fit",
            "Recommended Premium Brief",
            "Review my shortlist",
            "Estimate your retirement capital",
            "Representative property",
            "Asking price",
        ):
            self.assertNotIn(forbidden, self.japan)

    def test_japan_renders_one_destination_comparison_with_dossier_links(self) -> None:
        self.assertEqual(1, self.japan.count('id="destinations"'))
        self.assertEqual(1, self.japan.count('class="foreign-buyer-destination-table"'))
        for destination_id in ("fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"):
            self.assertIn(f"/destinations/{destination_id}/", self.japan)

    def test_metadata_targets_acquisition_intent(self) -> None:
        self.assertIn(
            "<title>Buying Property in Japan as a Foreigner | Global Home Atlas</title>",
            self.japan,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/countries/japan-property/">',
            self.japan,
        )
        description = re.search(
            r'<meta name="description" content="([^"]+)">', self.japan
        ).group(1)
        self.assertLessEqual(len(description), 160)
        self.assertIn("foreigners", description.lower())
        self.assertNotIn("retirement property", description.lower())

    def test_visible_faq_and_destination_rows_match_acquisition_schema(self) -> None:
        schema_text = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            self.japan,
            flags=re.DOTALL,
        ).group(1)
        schemas = json.loads(schema_text)
        schema_types = [item.get("@type") for item in schemas]
        self.assertIn("Article", schema_types)
        self.assertIn("FAQPage", schema_types)
        self.assertIn("ItemList", schema_types)
        article = next(item for item in schemas if item.get("@type") == "Article")
        faq = next(item for item in schemas if item.get("@type") == "FAQPage")
        item_list = next(item for item in schemas if item.get("@type") == "ItemList")

        self.assertEqual(self.japan.count('class="foreign-buyer-faq-item"'), len(faq["mainEntity"]))
        self.assertEqual(4, len(item_list["itemListElement"]))
        self.assertEqual("Buying Property in Japan as a Foreigner", article["headline"])
        self.assertEqual("https://globalhomeatlas.com/countries/japan-property/", article["url"])
        for field in ("datePublished", "dateModified", "author", "publisher"):
            self.assertIn(field, article)
        self.assertNotIn("CollectionPage", schema_types)

    def test_country_guide_links_once_to_the_retirement_guide(self) -> None:
        href = '/japan-retirement-property-foreign-buyers/'
        self.assertEqual(1, self.japan.count(href))
        self.assertIn(
            "Planning to live in Japan long term? Read the",
            self.japan,
        )


class ForeignBuyerCountryGuideDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = render_country("japan-property")

    def test_page_uses_premium_editorial_typography_without_heavy_weights(self) -> None:
        self.assertIn("--foreign-buyer-serif:", self.html)
        self.assertIn(".foreign-buyer-hero h1", self.html)
        for weight in ("font-weight: 800", "font-weight: 850", "font-weight: 900"):
            self.assertNotIn(weight, self.html)

    def test_rail_and_mobile_targets_are_explicit(self) -> None:
        self.assertIn(".foreign-buyer-rail { position: sticky;", self.html)
        self.assertIn(".foreign-buyer-rail a { min-height: 44px;", self.html)
        self.assertIn("@media (max-width: 720px)", self.html)

    def test_comparison_has_desktop_table_and_mobile_cards(self) -> None:
        self.assertIn('class="foreign-buyer-destination-table"', self.html)
        self.assertIn('class="foreign-buyer-destination-cards"', self.html)
        self.assertIn(".foreign-buyer-destination-table { display: none;", self.html)

    def test_source_links_wrap_at_narrow_viewports(self) -> None:
        self.assertIn(
            ".foreign-buyer-source-links a { margin-right: 10px; overflow-wrap: anywhere; white-space: normal; }",
            self.html,
        )
        self.assertNotIn(".foreign-buyer-source-links a { margin-right: 10px; white-space: nowrap; }", self.html)

    def test_cost_table_stacks_labelled_rows_on_mobile(self) -> None:
        self.assertIn('data-label="When"', self.html)
        self.assertIn('data-label="What matters"', self.html)
        self.assertIn(".foreign-buyer-cost-table thead { position: absolute;", self.html)
        self.assertIn(".foreign-buyer-mobile-label { display: block;", self.html)
        self.assertNotIn(".foreign-buyer-cost-table { display: block; overflow-x: auto;", self.html)

    def test_mobile_cost_labels_are_real_text_with_accessible_headers(self) -> None:
        self.assertIn('<span class="foreign-buyer-mobile-label">When</span>', self.html)
        self.assertIn('<span class="foreign-buyer-mobile-label">What matters</span>', self.html)
        self.assertIn(".foreign-buyer-cost-table thead { position: absolute;", self.html)
        self.assertNotIn(".foreign-buyer-cost-table thead { display: none;", self.html)

    def test_rail_precedes_article_in_dom_and_mobile_target_rules_are_complete(self) -> None:
        self.assertLess(
            self.html.index('<aside class="foreign-buyer-rail">'),
            self.html.index('<article class="foreign-buyer-article">'),
        )
        self.assertNotIn(".foreign-buyer-rail { position: static; order: -1;", self.html)
        self.assertIn(".foreign-buyer-country-guide .gha-footer a { min-height: 44px;", self.html)
        self.assertIn(".foreign-buyer-destination-cards h3 a { min-height: 44px;", self.html)
