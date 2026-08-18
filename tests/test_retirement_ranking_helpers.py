from __future__ import annotations

import unittest

from src.build_unified_app import split_rankings


class RetirementRankingHelperTests(unittest.TestCase):
    def test_split_rankings_keeps_first_ten_visible(self) -> None:
        rankings = [{"rank": value} for value in range(1, 31)]
        visible, expandable = split_rankings(rankings)
        self.assertEqual(list(range(1, 11)), [item["rank"] for item in visible])
        self.assertEqual(list(range(11, 31)), [item["rank"] for item in expandable])

    def test_split_rankings_rejects_non_positive_visible_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "visible_count must be positive"):
            split_rankings([{"rank": 1}], visible_count=0)


if __name__ == "__main__":
    unittest.main()
