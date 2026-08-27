from __future__ import annotations

from collections import Counter
from copy import deepcopy
import unittest
from urllib.parse import urlsplit

from src.foreign_buyer_country_guides import (
    FOREIGN_BUYER_COUNTRY_GUIDES,
    get_foreign_buyer_country_guide,
    validate_foreign_buyer_country_guide,
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
            {"cost": f"Cost {index}", "when": "When", "buyer_read": "Read", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 5)
        ],
        "ownership_rules": [deepcopy(sourced)],
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


class JapanForeignBuyerSourceIntegrityTests(unittest.TestCase):
    approved_domains = {
        "mof.go.jp",
        "moj.go.jp",
        "mlit.go.jp",
        "nta.go.jp",
        "gsi.go.jp",
        "mofa.go.jp",
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
