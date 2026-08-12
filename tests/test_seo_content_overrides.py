from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src import seo_content_overrides


def valid_entry(target: str = "https://globalhomeatlas.com/buy-property-abroad/") -> dict:
    return {
        "target_url": target,
        "finding_fingerprint": "gha-low-ctr-opportunity-abc123",
        "base_content_hash": "a" * 64,
        "generated_at": "2026-08-12T00:00:00+00:00",
        "model": "test-model",
        "signal": {"impressions": 40},
        "lifecycle": "proposed",
        "cooldown_until": "2026-09-09T00:00:00+00:00",
        "content": {
            "title": "New title",
            "meta_description": "New description",
            "intro": "New intro",
            "faq_question": "New?",
            "faq_answer": "New answer.",
            "internal_link_target": "https://globalhomeatlas.com/guides/",
            "internal_link_anchor": "property buying guides",
        },
    }


class ContentOverrideRuntimeTests(unittest.TestCase):
    def test_apply_content_override_maps_only_recognized_fields(self) -> None:
        base = {"title": "Old", "description": "Old description", "faqs": [("Old?", "Old answer.")]}
        result = seo_content_overrides.apply_content_override(
            base,
            "https://globalhomeatlas.com/buy-property-abroad/",
            [valid_entry()],
        )
        self.assertEqual("New title", result["title"])
        self.assertEqual("New description", result["description"])
        self.assertEqual("New intro", result["generated_intro"])
        self.assertEqual(("New?", "New answer."), result["faqs"][-1])
        self.assertEqual("property buying guides", result["generated_internal_link"]["anchor"])
        self.assertEqual("Old", base["title"])

    def test_loader_rejects_unknown_fields(self) -> None:
        entry = valid_entry()
        entry["content"]["script"] = "alert(1)"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "overrides.json"
            path.write_text(json.dumps([entry]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "content fields"):
                seo_content_overrides.load_content_overrides(path)

    def test_loader_rejects_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "overrides.json"
            path.write_text(json.dumps([valid_entry(), valid_entry()]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                seo_content_overrides.load_content_overrides(path)

    def test_loader_rejects_unsupported_target_and_malformed_timestamp(self) -> None:
        unsupported = valid_entry("https://globalhomeatlas.com/about/")
        fabricated_country = valid_entry("https://globalhomeatlas.com/countries/not-rendered/")
        malformed = valid_entry()
        malformed["generated_at"] = "not-a-date"
        for entry, message in (
            (unsupported, "Unsupported"), (fabricated_country, "Unsupported"), (malformed, "timestamp")
        ):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as tmpdir:
                path = Path(tmpdir) / "overrides.json"
                path.write_text(json.dumps([entry]), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    seo_content_overrides.load_content_overrides(path)


if __name__ == "__main__":
    unittest.main()
