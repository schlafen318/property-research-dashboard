from __future__ import annotations

import unittest

from src import build_unified_app


class LandingDesignSystemPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = build_unified_app.build_landing_page([], [], [], 0)

    def test_landing_page_declares_the_pilot_mode_and_shared_foundation(self) -> None:
        self.assertIn('<body class="gha-mode-landing" data-design-system="gha-v1">', self.html)
        self.assertIn('--gha-ink: #24312d;', self.html)
        self.assertIn('--gha-display-serif:', self.html)
        self.assertEqual(1, self.html.count('data-design-system="gha-v1"'))

    def test_landing_page_uses_the_shared_header_and_footer(self) -> None:
        self.assertEqual(1, self.html.count('class="gha-header"'))
        self.assertEqual(1, self.html.count('class="gha-footer"'))
        self.assertIn('class="gha-primary-nav" aria-label="Primary"', self.html)
        self.assertIn('class="gha-mobile-menu"', self.html)

    def test_reader_facing_chrome_uses_regular_or_medium_weight(self) -> None:
        required_rules = (
            '.gha-primary-links a { font-weight: 500;',
            '.gha-mode-landing .primary-action { font-weight: 500;',
            '.gha-footer { font-weight: 400;',
        )
        for rule in required_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.html)
        for forbidden_weight in ("font-weight: 800", "font-weight: 850", "font-weight: 900"):
            with self.subTest(forbidden_weight=forbidden_weight):
                self.assertNotIn(forbidden_weight, self.html)

    def test_accessible_contrast_and_mobile_target_contracts_are_explicit(self) -> None:
        self.assertIn('--gha-link: #41665a;', self.html)
        self.assertIn('.gha-mode-landing .finder-result h3 a { color: var(--gha-ink);', self.html)
        self.assertIn('.gha-mode-landing .primary-action:hover { background: var(--gha-accent); color: var(--gha-paper);', self.html)
        self.assertIn('.gha-mode-landing .hero-secondary-actions a { min-height: 44px;', self.html)

    def test_page_has_one_banner_landmark_and_preserves_footer_copy(self) -> None:
        self.assertEqual(1, self.html.count('<header class="gha-header">'))
        self.assertNotIn('<header class="hero"', self.html)
        self.assertIn('<section class="hero" id="top" aria-labelledby="landing-title">', self.html)
        for copy in (
            "Research dashboard",
            "Independent research for overseas property decisions. Research only; verify legal, tax, immigration, and property advice locally.",
            "Ask to be notified when new destination research or country hubs are added.",
            "Email hello@globalhomeatlas.com",
        ):
            with self.subTest(copy=copy):
                self.assertIn(copy, self.html)

    def test_landing_sections_use_rules_instead_of_generic_card_boxes(self) -> None:
        self.assertIn('.gha-mode-landing .section { margin: 0; padding:', self.html)
        self.assertIn('border-top: 1px solid var(--gha-rule);', self.html)
        self.assertIn('border-radius: 0;', self.html)
        self.assertIn('box-shadow: none;', self.html)

    def test_existing_market_finder_and_tracking_contracts_remain(self) -> None:
        for marker in (
            'id="finderGoal"',
            'id="finderResults"',
            'id="finderDetailed"',
            'data-track="homepage_start_click"',
            'window.GHA.track("market_finder_change"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)

    def test_atlas_tools_and_research_links_remain_scannable_and_tappable(self) -> None:
        self.assertIn('.gha-mode-landing .atlas-tool-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));', self.html)
        self.assertIn('.gha-mode-landing .atlas-tool { min-height: 100%; display: grid; align-content: start;', self.html)
        self.assertIn('.gha-mode-landing .atlas-tool__link { min-height: 44px; display: inline-flex; align-items: center;', self.html)
        self.assertIn('.gha-mode-landing .research-link a { min-height: 44px; display: inline-flex; align-items: center;', self.html)

    def test_hero_copy_aligns_to_the_site_grid_without_a_redundant_eyebrow(self) -> None:
        self.assertIn(
            '.gha-mode-landing .hero-grid { width: min(790px, calc(100% - 48px)); max-width: none; margin: 0 auto 0 max(24px, calc((100% - 1220px) / 2));',
            self.html,
        )
        self.assertIn(
            '.gha-mode-landing .hero-grid { width: min(790px, calc(100% - 32px)); margin-left: 16px;',
            self.html,
        )
        self.assertNotIn('Independent overseas property research', self.html)
        self.assertNotIn('.gha-eyebrow', self.html)

    def test_landing_omits_the_redundant_shortlist_conversion_band(self) -> None:
        self.assertNotIn('id="conversion"', self.html)
        self.assertNotIn('Want help narrowing your shortlist?', self.html)
        self.assertNotIn('data-track="shortlist_review_click"', self.html)
        self.assertNotIn('.gha-mode-landing .cta-band', self.html)


if __name__ == "__main__":
    unittest.main()
