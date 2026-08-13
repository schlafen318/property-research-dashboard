from __future__ import annotations

import tempfile
import unittest
import json
import os
from dataclasses import replace
from pathlib import Path

from scripts import seo_content_generator


class ContextCollectionTests(unittest.TestCase):
    def test_collect_target_context_reads_metadata_intro_and_faqs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            page = root / "countries" / "portugal-property" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<title>Portugal Guide</title>'
                '<meta name="description" content="Current description">'
                '<link rel="canonical" href="https://globalhomeatlas.com/countries/portugal-property/">'
                '<h1>Portugal Property Guide</h1>'
                '<p class="page-lede">Current intro.</p>'
                '<details class="faq-item"><summary>Question?</summary><p>Answer.</p></details>',
                encoding="utf-8",
            )

            context = seo_content_generator.collect_target_context(
                "https://globalhomeatlas.com/countries/portugal-property/",
                ["https://globalhomeatlas.com/countries/portugal-property/"],
                artifacts_root=root,
            )

        self.assertEqual("country", context.page_type)
        self.assertEqual("Portugal Guide", context.title)
        self.assertEqual("Current description", context.meta_description)
        self.assertEqual("Portugal Property Guide", context.h1)
        self.assertEqual("Current intro.", context.intro)
        self.assertEqual((("Question?", "Answer."),), context.faqs)
        self.assertEqual(64, len(context.base_content_hash))

    def test_collect_target_context_rejects_url_outside_sitemap(self) -> None:
        with self.assertRaisesRegex(ValueError, "not present in sitemap"):
            seo_content_generator.collect_target_context(
                "https://globalhomeatlas.com/not-real/",
                ["https://globalhomeatlas.com/"],
                artifacts_root=Path("artifacts"),
            )

    def test_page_type_routes_known_paths(self) -> None:
        self.assertEqual("homepage", seo_content_generator.page_type_for_url("https://globalhomeatlas.com/"))
        self.assertEqual(
            "country",
            seo_content_generator.page_type_for_url("https://globalhomeatlas.com/countries/spain-property/"),
        )
        self.assertEqual(
            "destination",
            seo_content_generator.page_type_for_url("https://globalhomeatlas.com/destinations/andermatt/"),
        )
        self.assertEqual(
            "guide",
            seo_content_generator.page_type_for_url("https://globalhomeatlas.com/buy-property-abroad/"),
        )
        self.assertEqual(
            "guide",
            seo_content_generator.page_type_for_url("https://globalhomeatlas.com/where-can-foreigners-buy-property/"),
        )
        with self.assertRaisesRegex(ValueError, "not supported"):
            seo_content_generator.page_type_for_url("https://globalhomeatlas.com/about/")

    def test_homepage_lede_is_included_in_context_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            page = root / "index.html"
            page.write_text(
                '<title>Atlas</title><meta name="description" content="Description">'
                '<link rel="canonical" href="https://globalhomeatlas.com/">'
                '<h1>Research property markets</h1><p class="lede">Visible homepage intro.</p>',
                encoding="utf-8",
            )
            context = seo_content_generator.collect_target_context(
                "https://globalhomeatlas.com/", ["https://globalhomeatlas.com/"], artifacts_root=root
            )
        self.assertEqual("Visible homepage intro.", context.intro)


class ProposalValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = seo_content_generator.TargetPageContext(
            target_url="https://globalhomeatlas.com/countries/portugal-property/",
            page_type="country",
            title="Portugal Property Guide",
            meta_description="Compare Portugal property markets for foreign buyers and practical retirement planning.",
            h1="Portugal Property Guide",
            intro="Portugal is a retirement and second-home benchmark for foreign buyers.",
            faqs=(),
            sitemap_urls=(
                "https://globalhomeatlas.com/countries/portugal-property/",
                "https://globalhomeatlas.com/buy-property-abroad/",
            ),
            base_content_hash="a" * 64,
        )

    def proposal(self, **changes):
        values = {
            "finding_fingerprint": "gha-low-ctr-opportunity-abc123",
            "target_url": self.context.target_url,
            "base_content_hash": self.context.base_content_hash,
            "title": "Portugal Property Guide for Foreign Buyers",
            "meta_description": "Compare Portugal property markets for foreign buyers, retirement planning, and second-home research.",
            "intro": "Compare Portugal as a retirement and second-home benchmark for foreign buyers.",
            "faq_question": None,
            "faq_answer": None,
            "internal_link_target": "https://globalhomeatlas.com/buy-property-abroad/",
            "internal_link_anchor": "buying property abroad guide",
            "rationale": "Matches observed foreign-buyer query intent.",
            "source_fragments": ["Portugal", "retirement and second-home benchmark"],
            "policy_flags": {
                "legal": False,
                "tax": False,
                "visa": False,
                "ownership": False,
                "price": False,
                "yield": False,
                "return": False,
                "guarantee": False,
            },
        }
        values.update(changes)
        return seo_content_generator.proposal_from_dict(values)

    def test_valid_proposal_has_no_errors(self) -> None:
        self.assertEqual([], seo_content_generator.validate_proposal(self.proposal(), self.context))

    def test_rejects_new_number_and_prohibited_claim(self) -> None:
        proposal = self.proposal(intro="Portugal guarantees a 12% return for foreign buyers.")
        errors = seo_content_generator.validate_proposal(proposal, self.context)
        self.assertTrue(any("number" in error for error in errors))
        self.assertTrue(any("guarantee" in error or "return" in error for error in errors))

    def test_rejects_stale_hash_outside_link_and_country_faq(self) -> None:
        proposal = self.proposal(
            base_content_hash="b" * 64,
            internal_link_target="https://example.com/",
            faq_question="Is Portugal suitable?",
            faq_answer="Compare Portugal carefully.",
        )
        errors = seo_content_generator.validate_proposal(proposal, self.context)
        self.assertTrue(any("hash" in error for error in errors))
        self.assertTrue(any("sitemap" in error for error in errors))
        self.assertTrue(any("FAQ" in error for error in errors))

    def test_rejects_all_prohibited_claim_categories_deterministically(self) -> None:
        claims = {
            "legal": "This is legal for buyers.",
            "tax": "Buyers receive a tax advantage.",
            "visa": "This home includes a visa path.",
            "ownership": "Foreign buyers may own any home.",
            "price": "This is an affordable market.",
            "yield": "The market provides strong yield.",
            "return": "Buyers receive a strong return.",
            "guarantee": "This is a guaranteed choice.",
        }
        for category, intro in claims.items():
            with self.subTest(category=category):
                errors = seo_content_generator.validate_proposal(self.proposal(intro=intro), self.context)
                self.assertTrue(any(category in error for error in errors), errors)

    def test_rejects_protected_claim_even_when_category_word_exists_in_source(self) -> None:
        errors = seo_content_generator.validate_proposal(
            self.proposal(intro="Buyers have unrestricted ownership rights."), self.context
        )
        self.assertTrue(any("ownership" in error for error in errors), errors)

    def test_rejects_missing_evidence_new_entity_and_keyword_stuffing(self) -> None:
        repeated = "Portugal property guide Portugal property guide Portugal property guide Portugal property guide"
        proposal = self.proposal(
            intro=f"Lisbon Market research. {repeated}",
            source_fragments=[],
        )
        errors = seo_content_generator.validate_proposal(proposal, self.context)
        self.assertTrue(any("source fragment" in error for error in errors))
        self.assertTrue(any("capitalized entities" in error and "Lisbon Market" in error for error in errors))
        self.assertTrue(any("repeats" in error for error in errors))

    def test_entity_validation_ignores_sentence_starts_but_rejects_new_proper_names(self) -> None:
        ordinary = self.proposal(intro="More research helps buyers compare markets. Which market fits best?")
        ordinary_errors = seo_content_generator.validate_proposal(ordinary, self.context)
        self.assertFalse(any("capitalized entities" in error for error in ordinary_errors), ordinary_errors)

        unsupported = self.proposal(intro="Compare New York research with Portugal.")
        unsupported_errors = seo_content_generator.validate_proposal(unsupported, self.context)
        self.assertTrue(
            any("capitalized entities" in error and "New York" in error for error in unsupported_errors),
            unsupported_errors,
        )

    def test_entity_validation_accepts_supported_name_after_sentence_start_word(self) -> None:
        context = replace(
            self.context,
            intro="Portugal and New York are comparison benchmarks for foreign buyers.",
        )
        proposal = self.proposal(intro="Compare New York with Portugal for foreign-buyer research.")

        errors = seo_content_generator.validate_proposal(proposal, context)

        self.assertFalse(any("capitalized entities" in error for error in errors), errors)

    def test_entity_validation_rejects_names_with_connectors_and_abbreviations(self) -> None:
        introductions = (
            "Explore the Costa del Sol market with Portugal.",
            "Research in Rio de Janeiro alongside Portugal.",
            "Compare Côte d'Azur with Portugal.",
            "Compare St. Moritz with Portugal.",
        )

        for intro in introductions:
            with self.subTest(intro=intro):
                errors = seo_content_generator.validate_proposal(self.proposal(intro=intro), self.context)
                self.assertTrue(any("capitalized entities" in error for error in errors), errors)

    def test_upsert_override_deduplicates_target_and_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "overrides.json"
            path.write_text(
                json.dumps(
                    [
                        {"target_url": self.context.target_url, "finding_fingerprint": "old"},
                        {"target_url": "https://globalhomeatlas.com/other/", "finding_fingerprint": "same"},
                    ]
                ),
                encoding="utf-8",
            )
            entry = {
                "target_url": self.context.target_url,
                "finding_fingerprint": "same",
                "content": {},
            }
            seo_content_generator.upsert_override_entry(entry, path=path)
            rows = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual([entry], rows)


class FakeResponse:
    def __init__(self, payload: dict, status: str = "completed", output=None) -> None:
        self.status = status
        self.output = output or []
        self.output_text = json.dumps(payload)


class FakeResponses:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class FakeClient:
    def __init__(self, responses) -> None:
        self.responses = FakeResponses(responses)


class OpenAIGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = seo_content_generator.TargetPageContext(
            target_url="https://globalhomeatlas.com/countries/portugal-property/",
            page_type="country",
            title="Portugal Property Guide",
            meta_description="Compare Portugal property markets for foreign buyers and practical retirement planning.",
            h1="Portugal Property Guide",
            intro="Portugal is a retirement and second-home benchmark for foreign buyers.",
            faqs=(),
            sitemap_urls=(
                "https://globalhomeatlas.com/countries/portugal-property/",
                "https://globalhomeatlas.com/buy-property-abroad/",
            ),
            base_content_hash="a" * 64,
        )
        self.finding = {
            "fingerprint": "gha-low-ctr-opportunity-abc123",
            "kind": "low-ctr-opportunity",
            "payload": {"page": self.context.target_url, "impressions": 40, "position": 8.0},
        }
        self.valid_proposal = {
            "finding_fingerprint": self.finding["fingerprint"],
            "target_url": self.context.target_url,
            "base_content_hash": self.context.base_content_hash,
            "title": "Portugal Property Guide for Foreign Buyers",
            "meta_description": "Compare Portugal property markets for foreign buyers, retirement planning, and second-home research.",
            "intro": "Compare Portugal as a retirement and second-home benchmark for foreign buyers.",
            "faq_question": None,
            "faq_answer": None,
            "internal_link_target": "https://globalhomeatlas.com/buy-property-abroad/",
            "internal_link_anchor": "buying property abroad guide",
            "rationale": "Matches observed foreign-buyer query intent.",
            "source_fragments": ["Portugal", "retirement and second-home benchmark"],
            "policy_flags": {name: False for name in seo_content_generator.POLICY_FLAG_NAMES},
        }

    def test_generate_proposal_uses_strict_schema(self) -> None:
        client = FakeClient([FakeResponse(self.valid_proposal)])
        proposal = seo_content_generator.generate_proposal(
            self.finding,
            self.context,
            client=client,
            model="test-model",
        )
        request = client.responses.calls[0]
        self.assertEqual("test-model", request["model"])
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(seo_content_generator.PROPOSAL_JSON_SCHEMA, request["text"]["format"]["schema"])
        self.assertEqual(self.context.target_url, proposal.target_url)

    def test_generation_prompt_is_page_aware_and_length_bounded(self) -> None:
        messages = seo_content_generator.build_generation_input(self.finding, self.context)
        developer_message = messages[0]["content"]
        self.assertIn("country", developer_message)
        self.assertIn("FAQ fields must be null", developer_message)
        self.assertIn("30 to 65 characters", developer_message)
        self.assertIn("70 to 165 characters", developer_message)
        self.assertIn("protected-topic language must be null", developer_message)

    def test_generate_proposal_rejects_incomplete_response(self) -> None:
        client = FakeClient([FakeResponse(self.valid_proposal, status="incomplete")])
        with self.assertRaisesRegex(seo_content_generator.GenerationFailure, "incomplete"):
            seo_content_generator.generate_proposal(self.finding, self.context, client=client)

    def test_retry_recovers_from_transient_connection_error(self) -> None:
        client = FakeClient([ConnectionError("temporary"), FakeResponse(self.valid_proposal)])
        sleeps = []
        proposal = seo_content_generator.generate_proposal_with_retry(
            self.finding,
            self.context,
            client=client,
            attempts=3,
            sleep_fn=sleeps.append,
        )
        self.assertEqual(self.context.target_url, proposal.target_url)
        self.assertEqual([1], sleeps)

    def test_retry_recognizes_openai_connection_exception_names_without_importing_sdk(self) -> None:
        api_connection_error = type("APIConnectionError", (Exception,), {})
        client = FakeClient([api_connection_error("temporary"), FakeResponse(self.valid_proposal)])
        sleeps = []
        proposal = seo_content_generator.generate_proposal_with_retry(
            self.finding, self.context, client=client, attempts=2, sleep_fn=sleeps.append
        )
        self.assertEqual(self.context.target_url, proposal.target_url)
        self.assertEqual([1], sleeps)

    def test_batch_skips_without_api_key(self) -> None:
        original = os.environ.pop("OPENAI_API_KEY", None)
        try:
            result = seo_content_generator.generate_batch([(self.finding, self.context)])
        finally:
            if original is not None:
                os.environ["OPENAI_API_KEY"] = original
        self.assertEqual("OPENAI_API_KEY is not configured", result.skipped_reason)
        self.assertEqual((), result.accepted)

    def test_batch_keeps_valid_item_when_another_is_rejected(self) -> None:
        invalid = dict(self.valid_proposal, intro="Portugal guarantees a 12% return.")
        client = FakeClient([FakeResponse(invalid), FakeResponse(self.valid_proposal)])
        result = seo_content_generator.generate_batch(
            [(self.finding, self.context), (self.finding, self.context)],
            client=client,
            model="test-model",
            generated_at="2026-08-12T00:00:00+00:00",
        )
        self.assertEqual(1, len(result.accepted))
        self.assertEqual(1, len(result.rejected))

    def test_fixture_response_produces_one_override(self) -> None:
        fixtures = Path(__file__).parent / "fixtures"
        report = json.loads((fixtures / "seo-content-report.json").read_text(encoding="utf-8"))
        target = report["search_console"]["low_ctr_pages"][0]["page"]
        context = seo_content_generator.collect_target_context(
            target,
            report["sitemap"]["urls"],
        )
        response = json.loads((fixtures / "seo-content-response.json").read_text(encoding="utf-8"))
        response["base_content_hash"] = context.base_content_hash
        finding = {
            "fingerprint": response["finding_fingerprint"],
            "kind": "low-ctr-opportunity",
            "payload": report["search_console"]["low_ctr_pages"][0],
        }
        result = seo_content_generator.generate_batch(
            [(finding, context)],
            client=FakeClient([FakeResponse(response)]),
            model="test-model",
            generated_at="2026-08-12T00:00:00+00:00",
        )
        self.assertEqual(1, len(result.accepted))
        self.assertEqual(0, len(result.rejected))
        self.assertEqual(set(seo_content_generator.PROPOSAL_JSON_SCHEMA["properties"]) - {
            "finding_fingerprint", "target_url", "base_content_hash", "rationale", "source_fragments", "policy_flags"
        }, set(result.accepted[0]["content"]))


if __name__ == "__main__":
    unittest.main()
