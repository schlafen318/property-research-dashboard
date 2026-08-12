from __future__ import annotations

import tempfile
import unittest
import json
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


if __name__ == "__main__":
    unittest.main()
