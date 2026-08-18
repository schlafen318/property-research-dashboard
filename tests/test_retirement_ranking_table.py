from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "retirement_ranking_table.js"


class RetirementRankingTableTests(unittest.TestCase):
    def run_sort(self, key: str, direction: str) -> list[int]:
        rows = [
            {"rank": 1, "name": "Zulu", "annual": 60000, "savings": 1700000, "property": 900000},
            {"rank": 2, "name": "Alpha", "annual": 80000, "savings": 2300000, "property": 400000},
            {"rank": 3, "name": "Bravo", "annual": 70000, "savings": 2000000, "property": 600000},
        ]
        script = (
            f"const table = require({json.dumps(str(MODULE))});"
            f"const rows = {json.dumps(rows)};"
            f"console.log(JSON.stringify(table.sortRankingRows(rows, {json.dumps(key)}, {json.dumps(direction)}).map(row => row.rank)));"
        )
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_sorts_numeric_columns_in_both_directions(self) -> None:
        self.assertEqual([2, 3, 1], self.run_sort("property", "ascending"))
        self.assertEqual([1, 3, 2], self.run_sort("property", "descending"))

    def test_sorts_destination_names_alphabetically(self) -> None:
        self.assertEqual([2, 3, 1], self.run_sort("name", "ascending"))


if __name__ == "__main__":
    unittest.main()
