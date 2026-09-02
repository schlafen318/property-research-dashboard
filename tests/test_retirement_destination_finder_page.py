from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "retirement-destination-finder" / "index.html"


class RetirementDestinationFinderPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "src/build_unified_app.py"], cwd=ROOT, check=True, capture_output=True)
        cls.html = ARTIFACT.read_text()
        cls.builder = (ROOT / "src" / "build_unified_app.py").read_text()
        cls.retirement_count = len(
            json.loads((ROOT / "data" / "retirement_costs.json").read_text())["destinations"]
        )

    def test_route_has_canonical_and_reciprocal_mode_link(self) -> None:
        self.assertIn(
            "<title>Retirement Destination Finder: Where Can I Afford to Retire? | Global Home Atlas</title>",
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/retirement-destination-finder/">',
            self.html,
        )
        self.assertIn('href="/retirement-abroad-calculator/">Plan for a destination</a>', self.html)
        self.assertIn('aria-current="page">Find destinations I can afford</a>', self.html)

    def test_page_uses_shared_editorial_shell_and_final_design_layer(self) -> None:
        self.assertIn('<body class="gha-mode-utility retirement-finder-page" data-design-system="gha-v1">', self.html)
        self.assertIn('<header class="gha-header">', self.html)
        self.assertIn('class="gha-mobile-menu"', self.html)
        self.assertIn('<footer class="gha-footer">', self.html)
        self.assertNotIn('class="page-nav"', self.html)
        head = self.html.split("</head>", 1)[0]
        marker = '<style id="gha-retirement-finder-design">'
        self.assertEqual(head.rfind("<style"), head.index(marker))
        design_css = head.split(marker, 1)[1].split("</style>", 1)[0]
        self.assertIn('--gha-display-serif: "Iowan Old Style"', design_css)
        self.assertRegex(
            design_css,
            r"\.retirement-finder-page \.finder-section\s*\{[^}]*border-radius:\s*0;[^}]*\}",
        )
        self.assertRegex(
            design_css,
            r"\.retirement-finder-page input,[^{]*\{[^}]*border-radius:\s*0;[^}]*font-weight:\s*400;",
        )

    def test_calculator_mode_links_share_one_aligned_tab_treatment(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(
            ".gha-mode-utility .calc-modes, .gha-mode-utility .finder-modes",
            design_css,
        )
        self.assertIn(
            ".gha-mode-utility .calc-modes a, .gha-mode-utility .finder-modes a",
            design_css,
        )
        self.assertIn("text-decoration: none", design_css)
        self.assertIn("box-shadow: inset 0 -2px 0 var(--gha-accent)", design_css)

    def test_finder_uses_the_landing_page_left_grid_without_overstretching_content(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(
            ".retirement-finder-page .gha-shell, .retirement-finder-page .page-shell",
            design_css,
        )
        self.assertIn("width: min(1220px, calc(100% - 48px))", design_css)
        self.assertIn(
            ".retirement-finder-page .finder-form, .retirement-finder-page .finder-results, .retirement-finder-page .finder-editorial",
            design_css,
        )
        self.assertIn("max-width: 960px", design_css)

    def test_form_uses_top_down_human_reading_order(self) -> None:
        ordered_ids = [
            'id="finder-profile"',
            'id="finder-current-resources"',
            'id="finder-housing"',
            'id="finder-retirement-income"',
            'id="finder-preferences"',
            'id="finder-submit"',
            'id="finder-results"',
        ]
        positions = [self.html.index(value) for value in ordered_ids]
        self.assertEqual(sorted(positions), positions)

    def test_preference_copy_distinguishes_filters_from_ranking(self) -> None:
        preferences = self.html.split('id="finder-preferences"', 1)[1].split("</fieldset>", 1)[0]
        landscape = self.html.split('id="finder-capital-landscape"', 1)[1].split("</figure>", 1)[0]

        self.assertIn("Region and setting filter destinations", preferences)
        self.assertIn("healthcare ranks your best matches", preferences)
        self.assertIn("Destinations match your selected region and setting", landscape)

    def test_setting_filter_allows_multiple_clear_checkbox_selections(self) -> None:
        preferences = self.html.split('id="finder-preferences"', 1)[1].split("</fieldset>", 1)[0]

        self.assertIn('role="group" aria-labelledby="finder-setting-label"', preferences)
        self.assertEqual(4, preferences.count('name="finder-setting"'))
        for value in ("City", "CoastOrIsland", "Mountain", "Lake"):
            self.assertIn(f'name="finder-setting" value="{value}"', preferences)
        self.assertIn(
            "Choose one or more. Destinations matching any selected setting are shown.",
            preferences,
        )
        self.assertNotIn('id="finder-climate"', preferences)

    def test_results_show_recommendations_before_the_full_cost_landscape(self) -> None:
        results = self.html.split('id="finder-results"', 1)[1].split(
            'class="finder-editorial"', 1
        )[0]

        self.assertLess(
            results.index('id="finder-matches-section"'),
            results.index('id="finder-capital-landscape"'),
        )
        self.assertIn('id="finder-landscape-toggle"', results)

    def test_results_reserve_plain_text_for_active_filters(self) -> None:
        results = self.html.split('id="finder-results"', 1)[1].split(
            'class="finder-editorial"', 1
        )[0]

        self.assertIn('id="finder-active-filters"', results)

    def test_form_defaults_to_age_45_and_retirement_at_60(self) -> None:
        form = self.html.split('id="retirement-destination-finder-form"', 1)[1].split(
            "</form>", 1
        )[0]

        self.assertIn(
            'id="finder-current-age" type="number" min="18" max="90" value="45"',
            form,
        )
        self.assertIn(
            'id="finder-retirement-age" type="number" min="19" max="100" value="60"',
            form,
        )

    def test_housing_and_conditional_fields_exist(self) -> None:
        for option in (
            '<option value="rent">Rent a home</option>',
            '<option value="buy_now">Buy a home now</option>',
            '<option value="buy_retirement">Buy a home at retirement</option>',
            '<option value="own">Already own my retirement home</option>',
        ):
            self.assertIn(option, self.html)
        for field_id in (
            "finder-property-allocation",
            "finder-purchase-method",
            "finder-buyer-residency",
            "finder-income-source",
            "finder-requested-ltv",
            "finder-mortgage-rate",
            "finder-mortgage-term",
            "finder-use-before-retirement",
            "finder-rental-yield",
            "finder-vacancy-rate",
            "finder-operating-cost-rate",
            "finder-mortgage-treatment",
        ):
            self.assertIn(f'id="{field_id}"', self.html)
        self.assertIn('<option value="not_sure">Not decided</option>', self.html)

    def test_results_are_concise_and_accessible(self) -> None:
        self.assertIn('id="finder-within-count"', self.html)
        self.assertIn('id="finder-eligible-count"', self.html)
        self.assertIn('id="finder-strongest-match"', self.html)
        self.assertIn('id="finder-capital-landscape"', self.html)
        self.assertIn('id="finder-landscape-projected"', self.html)
        self.assertIn('aria-labelledby="finder-landscape-heading finder-landscape-caption"', self.html)
        self.assertIn('id="finder-landscape-rows" role="list"', self.html)
        self.assertIn(
            'id="finder-projection" role="img" aria-labelledby="finder-projection-title finder-projection-desc"',
            self.html,
        )
        self.assertIn('<title id="finder-projection-title">Projected retirement portfolio</title>', self.html)
        self.assertIn('<desc id="finder-projection-desc">Complete the finder to see annual progression.</desc>', self.html)
        self.assertIn('id="finder-chart-target" x1="22" x2="618"', self.html)
        self.assertIn('id="finder-chart-target-label" x="618" text-anchor="end"', self.html)
        self.assertIn('id="finder-chart-tooltip" role="status"', self.html)
        self.assertIn('id="finder-projection-caption"', self.html)
        self.assertIn('id="finder-recommendations"', self.html)
        self.assertIn('id="finder-exclusions"', self.html)
        self.assertIn("Where your plan could take you", self.html)
        self.assertIn("Destinations shown", self.html)
        self.assertIn("Capital needed by destination", self.html)
        self.assertIn("All filtered destinations · lowest capital first", self.html)
        self.assertIn("How your capital could grow", self.html)
        self.assertNotIn("Retirement score", self.html)

    def test_results_include_compact_comparison_and_privacy_safe_sharing(self) -> None:
        for marker in (
            'id="finder-comparison"',
            'id="finder-comparison-body"',
            'id="finder-comparison-status" aria-live="polite"',
            'id="finder-share"',
            'id="finder-share-status" aria-live="polite"',
            'id="finder-shared-error" role="alert"',
        ):
            self.assertIn(marker, self.html)
        self.assertIn("Compare your strongest matches", self.html)
        self.assertIn(
            "This link includes your projected capital and planning choices. It does not include your age, current savings, income or pension details.",
            self.html,
        )
        self.assertIn("retirement_finder_scenario.js", self.builder)
        self.assertNotIn("algorithm", self.html.lower())

    def test_shared_query_is_removed_before_analytics_loads(self) -> None:
        scrub = 'window.__ghaFinderScenario'
        analytics = 'googletagmanager.com/gtag/js'
        self.assertIn(scrub, self.html)
        self.assertLess(self.html.index(scrub), self.html.index(analytics) if analytics in self.html else self.html.index('type="application/ld+json"'))
        self.assertIn('id="finder-data-reviewed"', self.html)

    def test_results_lead_with_three_modeled_matches_and_offer_the_cost_landscape(self) -> None:
        self.assertIn('id="finder-result-read"', self.html)
        self.assertIn('id="finder-recommendations"', self.html)
        self.assertIn('aria-label="Your three strongest matches"', self.html)
        self.assertNotIn('id="finder-closest-match"', self.html)
        self.assertNotIn('id="finder-show-all"', self.html)
        self.assertIn('id="finder-landscape-toggle"', self.html)
        self.assertIn("Destination guide", self.html)
        self.assertIn('data-finder-dossier', self.html)

    def test_landscape_uses_plain_editorial_rules_and_a_compact_mobile_list(self) -> None:
        self.assertIn('id="finder-landscape-heading">Capital needed by destination</h3>', self.html)
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(".retirement-finder-page .finder-landscape", design_css)
        self.assertIn("border-top: 1px solid var(--gha-rule)", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-row", design_css)
        self.assertIn("grid-template-columns: minmax(190px, 1.15fr) minmax(360px, 3fr) auto", design_css)
        self.assertIn("@media (max-width: 620px)", design_css)
        self.assertIn("grid-template-columns: minmax(0, 1fr) auto", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-projection", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-fill", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-cost-dot", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-plan-marker", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-required", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-buffer", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-row.is-within .finder-landscape-fill", design_css)
        self.assertIn(".retirement-finder-page .finder-landscape-row.is-over .finder-landscape-fill", design_css)
        self.assertIn("@media (max-width: 760px)", design_css)
        self.assertIn("@media (max-width: 820px)", design_css)
        self.assertIn(
            ".retirement-finder-page .finder-landscape-row { grid-template-columns: minmax(0, 1fr) minmax(120px, auto);",
            design_css,
        )
        self.assertIn(
            ".finder-landscape-rows:not(.is-expanded) > .finder-landscape-item:nth-child(n + 6)",
            design_css,
        )
        self.assertIn(".finder-landscape-toggle", design_css)
        self.assertNotIn("background: linear-gradient(to right", design_css)
        self.assertNotIn("border-left: 1px solid var(--gha-rule); border-right: 1px solid var(--gha-rule)", design_css)
        self.assertNotIn(".finder-landscape { border-radius:", design_css)

    def test_projection_does_not_force_results_wider_than_the_mobile_viewport(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(".retirement-finder-page .finder-results > * { min-width: 0; }", design_css)

    def test_match_headings_wrap_safely_in_the_three_column_layout(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(
            ".retirement-finder-page .finder-result h3 a { color: var(--gha-ink); font-weight: 400; white-space: normal; overflow-wrap: anywhere; }",
            design_css,
        )

    def test_results_include_a_dedicated_zero_eligible_state(self) -> None:
        self.assertIn('id="finder-empty-state"', self.html)
        self.assertIn('id="finder-matches-section"', self.html)
        self.assertIn('id="finder-projection-section"', self.html)

    def test_page_adds_specific_search_supporting_content_and_faq_schema(self) -> None:
        self.assertIn('id="how-matching-works"', self.html)
        self.assertIn('id="within-reach"', self.html)
        self.assertIn('id="rent-or-buy"', self.html)
        self.assertIn('id="finder-faq"', self.html)
        self.assertIn("Projected liquid capital covers the required retirement capital", self.html)
        self.assertIn("Buying requires separate property capital", self.html)
        self.assertIn('"@type":"FAQPage"', self.html)

    def test_mobile_navigation_and_results_use_touch_sized_controls(self) -> None:
        self.assertIn(".mobile-menu>nav{position:absolute", self.html)
        self.assertIn(".mobile-menu>nav a{display:flex;min-height:44px", self.html)
        self.assertIn(".finder-result header a{display:flex;min-height:44px", self.html)
        self.assertIn(".finder-results{min-width:0", self.html)
        self.assertIn(".finder-projection-wrap{min-width:0", self.html)
        self.assertIn(".finder-comparison-mobile", self.html)
        self.assertIn(
            ".retirement-finder-page .finder-setting-options .check { min-height: 44px;",
            self.html,
        )

    def test_mobile_hero_is_compact_enough_to_reach_the_form_quickly(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]

        self.assertIn("padding: 24px 0 26px", design_css)
        self.assertIn("font-size: clamp(38px, 11vw, 52px)", design_css)

    def test_mobile_wizard_renders_accessible_fixed_navigation(self) -> None:
        self.assertIn(
            'id="finder-wizard-progressbar" role="progressbar" aria-label="Retirement plan progress"',
            self.html,
        )
        self.assertIn('id="finder-wizard-back" type="button"', self.html)
        self.assertIn('id="finder-wizard-next" type="button">Continue</button>', self.html)
        self.assertIn('id="finder-adjust-plan" type="button" hidden>Adjust my plan</button>', self.html)
        self.assertIn('aria-valuemax="5"', self.html)

        design_css = self.html.split('<style id="gha-retirement-finder-design">', 1)[1].split(
            "</style>", 1
        )[0]
        mobile_css = design_css.split("@media (max-width: 760px)", 1)[1].split(
            "@media (max-width: 620px)", 1
        )[0]
        self.assertRegex(
            mobile_css,
            r"\.retirement-finder-page \.finder-wizard-actions\s*\{[^}]*display:\s*grid;[^}]*position:\s*fixed;",
        )
        self.assertIn("env(safe-area-inset-bottom)", mobile_css)
        self.assertRegex(
            mobile_css,
            r"\.retirement-finder-page \.finder-wizard-actions button\s*\{[^}]*min-height:\s*48px;",
        )

    def test_mobile_wizard_uses_a_focused_app_shell_while_editing(self) -> None:
        design_css = self.html.split('<style id="gha-retirement-finder-design">', 1)[1].split(
            "</style>", 1
        )[0]
        mobile_css = design_css.split("@media (max-width: 760px)", 1)[1].split(
            "@media (max-width: 620px)", 1
        )[0]

        self.assertIn(".retirement-finder-page.finder-wizard-editing", mobile_css)
        self.assertIn("overflow: hidden", mobile_css)
        self.assertIn(".finder-wizard-editing .finder-hero", mobile_css)
        self.assertIn(".finder-wizard-editing .finder-editorial", mobile_css)
        self.assertIn(".finder-wizard-editing .context-link", mobile_css)
        self.assertIn(".finder-wizard-editing .gha-footer", mobile_css)
        self.assertIn("display: none", mobile_css)
        self.assertRegex(
            mobile_css,
            r"\.finder-wizard-editing \.finder-section\s*\{[^}]*overflow-y:\s*auto;",
        )

    def test_mobile_wizard_keeps_compact_site_navigation_available(self) -> None:
        design_css = self.html.split('<style id="gha-retirement-finder-design">', 1)[1].split(
            "</style>", 1
        )[0]
        mobile_css = design_css.split("@media (max-width: 760px)", 1)[1].split(
            "@media (max-width: 620px)", 1
        )[0]

        self.assertIn('href="/retirement-abroad-calculator/">Retirement Calculator</a>', self.html)
        self.assertNotRegex(
            mobile_css,
            r"\.finder-wizard-editing \.gha-mobile-menu\s*\{[^}]*display:\s*none;",
        )

    def test_short_mobile_viewports_pair_compact_fields_to_avoid_step_scrolling(self) -> None:
        design_css = self.html.split('<style id="gha-retirement-finder-design">', 1)[1].split(
            "</style>", 1
        )[0]
        self.assertIn(
            ".finder-wizard-editing #finder-profile .field-grid",
            design_css,
        )
        self.assertIn(
            ".finder-wizard-editing #finder-current-resources .field-grid",
            design_css,
        )
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", design_css)
        self.assertIn("#finder-current-resources .field:last-child", design_css)
        self.assertIn("grid-column: 1 / -1", design_css)
        self.assertIn(
            ".finder-wizard-editing #finder-preferences .field-grid",
            design_css,
        )
        self.assertIn(
            ".finder-section-conditional > [data-finder-group] { margin-top: 0; padding-top: 0; border-top: 0; }",
            design_css,
        )
        self.assertIn("@media (max-width: 620px) and (max-height: 600px)", design_css)
        self.assertIn(
            ".finder-wizard-editing #finder-profile #finder-currency-note { display: none; }",
            design_css,
        )
        self.assertIn("font-size: 14px", design_css)

        form = self.html.split('id="retirement-destination-finder-form"', 1)[1].split(
            "</form>", 1
        )[0]
        self.assertIn("Rates dated 27 August 2026. Currency changes display values only.", form)

    def test_mobile_wizard_has_five_input_steps_and_results_plan_summary(self) -> None:
        form = self.html.split('id="retirement-destination-finder-form"', 1)[1].split(
            "</form>", 1
        )[0]

        for section_id in (
            "finder-profile",
            "finder-current-resources",
            "finder-housing",
            "finder-financing",
            "finder-before-retirement",
            "finder-retirement-income",
            "finder-preferences",
        ):
            self.assertIn(f'id="{section_id}"', form)
        self.assertNotIn('id="finder-review"', form)
        results = self.html.split('id="finder-results"', 1)[1].split("</section>", 1)[0]
        self.assertIn('id="finder-plan-summary"', results)
        self.assertIn('id="finder-review-retirement"', results)
        self.assertIn('id="finder-review-capital"', results)
        self.assertIn('id="finder-review-income"', results)
        self.assertIn('id="finder-review-preferences"', results)
        self.assertIn(
            'matchMedia("(max-width: 760px) and (orientation: portrait)")',
            self.html,
        )
        self.assertIn(
            ".finder-wizard-editing .finder-form > .finder-submit { display: none; }",
            self.html,
        )

    def test_desktop_labels_include_tax_as_the_fourth_of_five_steps(self) -> None:
        form = self.html.split('id="retirement-destination-finder-form"', 1)[1].split(
            "</form>", 1
        )[0]
        design_css = self.html.split('<style id="gha-retirement-finder-design">', 1)[1].split(
            "</style>", 1
        )[0]
        mobile_css = design_css.split("@media (max-width: 760px)", 1)[1].split(
            "@media (max-width: 620px)", 1
        )[0]

        self.assertIn('class="finder-step finder-step-desktop">Step 1 of 5', form)
        self.assertIn('class="finder-step finder-step-desktop">Step 4 of 5', form)
        self.assertNotIn("Step 5 of 6", form)
        self.assertIn('class="finder-desktop-only">What you have today', form)
        self.assertIn('class="finder-section finder-section-split"', form)
        self.assertIn(".finder-step.finder-step-mobile, .retirement-finder-page .finder-mobile-only { display: none; }", design_css)
        self.assertIn(".finder-profile", design_css)
        self.assertIn(".finder-section-split", design_css)
        self.assertIn(".finder-step-desktop", mobile_css)
        self.assertIn(".finder-step-mobile", mobile_css)

    def test_tax_choice_radios_do_not_inherit_full_width_input_styles(self) -> None:
        self.assertIn(".tax-mode-choice input{width:20px;min-height:20px", self.html)

    def test_projection_uses_editorial_svg_styles_instead_of_flex_bars(self) -> None:
        self.assertNotIn(".finder-projection-bars{height:180px;display:flex", self.html)
        self.assertIn('<div class="finder-projection-scroll">', self.html)
        self.assertIn(".finder-projection-scroll{overflow-x:auto", self.html)
        self.assertIn(".finder-projection-chart{display:block;width:100%;height:auto", self.html)
        self.assertIn("min-width:640px", self.html)
        self.assertIn(".finder-chart-bar{fill:#315e50", self.html)
        self.assertIn(".finder-chart-target{stroke:#9b6a33", self.html)
        self.assertIn("@media(prefers-reduced-motion:reduce)", self.html)
        self.assertIn(
            ".retirement-finder-page .finder-evidence summary { min-height: 44px; display: flex; align-items: center; font-weight: 500; }",
            self.html,
        )

    def test_embeds_complete_dynamic_universe(self) -> None:
        self.assertIn(f'data-universe-count="{self.retirement_count}"', self.html)
        self.assertNotIn("All 30 current destinations", self.html)
        self.assertNotIn('RETIREMENT_FINDER_DESTINATION_COUNT = 30', self.builder)
        for region in ("Asia", "Europe", "North America", "Oceania"):
            self.assertIn(f">{region}</option>", self.html)

    def test_page_explains_financing_evidence_and_privacy(self) -> None:
        self.assertIn("Mortgage availability is indicative", self.html)
        self.assertIn("Your financial details stay in this browser", self.html)
        self.assertIn('id="finder-financing-evidence"', self.html)

    def test_sitemap_contains_route(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text()
        self.assertIn("https://globalhomeatlas.com/retirement-destination-finder/", sitemap)

    def test_existing_retirement_journey_links_back_to_discovery(self) -> None:
        calculator = (ROOT / "artifacts" / "retirement-abroad-calculator" / "index.html").read_text()
        homepage = (ROOT / "artifacts" / "index.html").read_text()
        ranking = (ROOT / "artifacts" / "retirement-destinations-ranked-by-cost" / "index.html").read_text()
        expected = 'href="/retirement-destination-finder/"'
        self.assertIn(expected, calculator)
        self.assertIn(expected, homepage)
        self.assertIn(expected, ranking)

    def test_finder_embeds_the_shared_planning_currency_reference_data(self) -> None:
        payload = json.loads(
            self.html.split('<script type="application/json" id="retirement-finder-data">', 1)[1]
            .split("</script>", 1)[0]
        )

        self.assertEqual("2026-08-27", payload["planning_currencies"]["as_of"])
        self.assertEqual(
            ["USD", "EUR", "GBP", "CAD", "AUD", "CHF", "JPY", "HKD", "SGD"],
            list(payload["planning_currencies"]["rates_to_usd"]),
        )

    def test_finder_money_controls_follow_the_selected_planning_currency(self) -> None:
        self.assertIn(
            '<select id="finder-currency"><option value="USD" selected>USD — US dollar</option>',
            self.html,
        )
        self.assertIn('<option value="SGD">SGD — Singapore dollar</option>', self.html)
        self.assertIn(
            "Reference rates dated 27 August 2026. This changes the presentation currency, not future currency-risk assumptions.",
            self.html,
        )
        for field_id in (
            "finder-liquid-capital",
            "finder-monthly-contribution",
            "finder-property-allocation",
            "finder-pension",
            "finder-other-income",
        ):
            self.assertRegex(
                self.html,
                rf'<input id="{field_id}" type="text" inputmode="numeric" data-money min="\d+" step="\d+" value="[\d,]+"',
            )
        self.assertNotIn("(USD)", self.html)

    def test_finder_retirement_income_is_monthly_and_inflation_linked_by_default(self) -> None:
        self.assertIn("Income in retirement", self.html)
        self.assertIn("Monthly pension", self.html)
        self.assertIn("Other reliable monthly income", self.html)
        self.assertIn('<input id="finder-pension-indexed" type="checkbox" checked>', self.html)
        self.assertIn('<input id="finder-other-income-indexed" type="checkbox" checked>', self.html)

    def test_finder_result_grid_uses_a_valid_three_column_declaration(self) -> None:
        self.assertIn(
            ".finder-result dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px",
            self.html,
        )
        self.assertNotIn(
            "<style>.finder-result dl{grid-template-columns:repeat(3,minmax(0,1fr));}</style>",
            self.html,
        )


if __name__ == "__main__":
    unittest.main()
