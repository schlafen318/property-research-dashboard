from __future__ import annotations

import unittest

from scripts import seo_monitor


class SearchConsoleCompletenessTests(unittest.TestCase):
    def test_full_result_page_is_not_complete(self) -> None:
        self.assertFalse(seo_monitor.result_set_complete([{}] * 25, 25))

    def test_short_result_page_is_complete(self) -> None:
        self.assertTrue(seo_monitor.result_set_complete([{}] * 24, 25))

    def test_reconciliation_limit_uses_search_console_maximum(self) -> None:
        args = seo_monitor.parse_args([])
        self.assertEqual(25, args.row_limit)
        self.assertEqual(25000, args.reconciliation_row_limit)


if __name__ == "__main__":
    unittest.main()
