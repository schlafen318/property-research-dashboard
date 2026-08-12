from __future__ import annotations

import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
