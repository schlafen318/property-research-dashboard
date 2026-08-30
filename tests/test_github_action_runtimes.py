from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

NODE_24_ACTIONS = {
    "actions/checkout": "v7",
    "actions/setup-node": "v7",
    "actions/setup-python": "v7",
    "actions/configure-pages": "v6",
    "actions/upload-pages-artifact": "v5",
    "actions/deploy-pages": "v5",
    "actions/upload-artifact": "v7",
}


class GitHubActionRuntimeTests(unittest.TestCase):
    def test_workflows_use_node_24_action_majors(self) -> None:
        workflow_dir = ROOT / ".github" / "workflows"
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8") for path in workflow_dir.glob("*.yml")
        )

        for action, major in NODE_24_ACTIONS.items():
            with self.subTest(action=action):
                references = [
                    line.strip()
                    for line in workflow_text.splitlines()
                    if f"uses: {action}@" in line
                ]
                self.assertTrue(references, f"No workflow references {action}")
                self.assertTrue(
                    all(reference == f"uses: {action}@{major}" for reference in references),
                    f"Expected every {action} reference to use its Node 24 major {major}: "
                    + ", ".join(references),
                )


if __name__ == "__main__":
    unittest.main()
