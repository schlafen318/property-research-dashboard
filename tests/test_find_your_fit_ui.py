from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_MODULE = ROOT / "src" / "site_assets" / "find-your-fit-ui.js"


def run_node(script: str) -> object:
    result = subprocess.run(
        ["node", "-e", script, str(UI_MODULE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class FindYourFitUITests(unittest.TestCase):
    def test_setting_inputs_allow_multiple_choices_and_keep_any_exclusive(self) -> None:
        script = r"""
const ui = require(process.argv[1]);
function checkbox(value, checked) {
  return {
    value,
    checked,
    listeners: {},
    addEventListener(name, handler) { this.listeners[name] = handler; },
    change(checked) { this.checked = checked; this.listeners.change(); },
  };
}
const inputs = [
  checkbox("any", true),
  checkbox("city", false),
  checkbox("coast-island", false),
  checkbox("mountain", false),
  checkbox("lake", false),
];
ui.initSettingInputs(inputs);
const selected = () => inputs.filter((input) => input.checked).map((input) => input.value);
inputs[1].change(true);
const afterCity = selected();
inputs[4].change(true);
const afterLake = selected();
inputs[0].change(true);
const afterAny = selected();
inputs[0].change(false);
const afterClearingAny = selected();
inputs[1].change(true);
inputs[1].change(false);
const afterClearingLastConcrete = selected();
process.stdout.write(JSON.stringify({
  afterCity,
  afterLake,
  afterAny,
  afterClearingAny,
  afterClearingLastConcrete,
}));
"""

        self.assertEqual(
            {
                "afterCity": ["city"],
                "afterLake": ["city", "lake"],
                "afterAny": ["any"],
                "afterClearingAny": ["any"],
                "afterClearingLastConcrete": ["any"],
            },
            run_node(script),
        )

    def test_setting_helpers_apply_or_matching_and_report_each_match(self) -> None:
        script = r"""
const ui = require(process.argv[1]);
process.stdout.write(JSON.stringify({
  city: ui.settingScore(3.25, ["city", "coast-island"], ["city", "lake"]),
  lake: ui.settingScore(3.25, ["mountain", "lake"], ["city", "lake"]),
  mountain: ui.settingScore(3.25, ["mountain"], ["city", "lake"]),
  any: ui.settingScore(3.25, ["mountain"], ["any"]),
  matches: ui.matchingSettings(["city", "coast-island"], ["city", "coast-island", "lake"]),
}));
"""

        self.assertEqual(
            {
                "city": 5,
                "lake": 5,
                "mountain": 2,
                "any": 3.25,
                "matches": ["city", "coast-island"],
            },
            run_node(script),
        )


if __name__ == "__main__":
    unittest.main()
