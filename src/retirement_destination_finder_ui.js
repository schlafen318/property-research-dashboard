(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementDestinationFinderUI = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

  function housingVisibility(input) {
    const buyNow = input.housingPlan === "buy_now";
    return {
      buyNow: buyNow,
      mortgage: buyNow && ["mortgage", "not_sure"].includes(input.purchaseMethod),
      rental: buyNow && input.useBeforeRetirement === "rental",
      buyAtRetirement: input.housingPlan === "buy_retirement",
    };
  }

  function taxControlVisibility(input) {
    const estimate = String(input && input.taxMode || "destination_estimate") === "destination_estimate";
    const housingPlan = String(input && input.housingPlan || "rent");
    return {
      estimate: estimate,
      propertyUse: estimate && housingPlan !== "rent",
      wealthBand: estimate && Boolean(input && input.wealthTaxRelevant),
      afterTax: !estimate,
    };
  }

  function safeDetailHref(input) {
    const destinations = /^[a-z0-9-]+$/;
    const households = new Set(["single", "couple"]);
    const housing = new Set(["rent", "own", "buy_now", "buy_retirement"]);
    const destinationId = destinations.test(String(input.destinationId || ""))
      ? String(input.destinationId)
      : "";
    const household = households.has(input.household) ? input.household : "couple";
    const housingPlan = housing.has(input.housingPlan) ? input.housingPlan : "rent";
    return "/retirement-abroad-calculator/?destination=" + encodeURIComponent(destinationId) +
      "&household=" + encodeURIComponent(household) +
      "&housing=" + encodeURIComponent(housingPlan);
  }

  function safeDossierHref(destinationId) {
    const slug = /^[a-z0-9-]+$/.test(String(destinationId || "")) ? String(destinationId) : "";
    return "/destinations/" + (slug ? encodeURIComponent(slug) + "/" : "");
  }

  function recommendationsForDisplay(input) {
    const items = Array.isArray(input.items) ? input.items : [];
    return items.slice(0, input.expanded ? 12 : 5);
  }

  function resultSummaryRead(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const closest = recommendations[0];
    if (!closest) return "No destinations could be evaluated under these assumptions.";
    if (Number(input.withinReachCount) > 0) {
      return Number(input.withinReachCount) + " destinations are within reach. " +
        closest.name + " is the strongest modeled match under your preferences.";
    }
    return "No destinations are within reach yet. " + closest.name +
      " is the closest modeled match, with a gap of " + money.format(Math.abs(Number(closest.surplusGap))) + ".";
  }

  function tierLabel(value) {
    return {
      within_reach: "Within reach",
      close: "Close",
      stretch: "Stretch",
    }[value] || "Not classified";
  }

  function chartTooltip(point) {
    const heading = "Year " + Number(point.year);
    const value = money.format(Number(point.portfolio));
    return {
      heading: heading,
      value: value,
      accessibleLabel: heading + ", projected portfolio " + value + ".",
    };
  }

  function mobileChartWidth(pointCount) {
    const count = Math.max(1, Math.floor(Number(pointCount) || 0));
    return count * 44 + (count - 1) * 5;
  }

  function escapeHtml(value) {
    return String(value === null || value === undefined ? "" : value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character];
    });
  }

  function initRetirementDestinationFinder(rootId, payload) {
    if (!root) return;
    const container = document.getElementById(rootId);
    if (!container) return;
    const form = document.getElementById("retirement-destination-finder-form");
    const results = document.getElementById("finder-results");
    const errorSummary = document.getElementById("finder-errors");
    let currentRecommendations = [];
    let currentUser = null;
    let recommendationsExpanded = false;

    function element(id) { return document.getElementById(id); }
    function numeric(id) { return Number(element(id).value); }
    function checked(id) { return element(id).checked; }
    function selected(id) { return element(id).value; }
    function track(name, fields) {
      if (root.GHA && typeof root.GHA.track === "function") root.GHA.track(name, fields || {});
    }

    function selectedTaxMode() {
      const control = form.querySelector('input[name="finder-tax-mode"]:checked');
      return control ? control.value : "destination_estimate";
    }

    function finderHasWealthTaxEvidence() {
      const countries = payload.taxPlanning && payload.taxPlanning.countries || {};
      return Object.values(countries).some(function (country) {
        const screen = country && country.tax_screen || {};
        const allowance = screen.annual_allowances && screen.annual_allowances.wealth_tax;
        return allowance && ["favorable_usd", "central_usd", "adverse_usd"].some(function (key) {
          return Number(allowance[key]) > 0;
        });
      });
    }

    function syncTaxControls() {
      const visibility = taxControlVisibility({
        taxMode: selectedTaxMode(),
        housingPlan: selected("finder-housing-plan"),
        wealthTaxRelevant: finderHasWealthTaxEvidence(),
      });
      element("finder-tax-estimate-fields").hidden = !visibility.estimate;
      element("finder-tax-after-tax-note").hidden = !visibility.afterTax;
      element("finder-tax-property-use-field").hidden = !visibility.propertyUse;
      element("finder-tax-property-use").disabled = !visibility.propertyUse;
      element("finder-tax-wealth-band-field").hidden = !visibility.wealthBand;
      element("finder-tax-wealth-band").disabled = !visibility.wealthBand;
      ["finder-tax-withdrawals", "finder-tax-gain-intensity"].forEach(function (id) {
        element(id).disabled = !visibility.estimate;
      });
    }

    function syncHousing() {
      const visible = housingVisibility({
        housingPlan: selected("finder-housing-plan"),
        purchaseMethod: selected("finder-purchase-method"),
        residency: selected("finder-buyer-residency"),
        incomeSource: selected("finder-income-source"),
        useBeforeRetirement: selected("finder-use-before-retirement"),
      });
      document.querySelectorAll("[data-finder-group]").forEach(function (group) {
        group.hidden = !visible[group.dataset.finderGroup];
      });
      element("finder-own-guidance").hidden = selected("finder-housing-plan") !== "own";
      element("finder-submit").disabled = selected("finder-housing-plan") === "own";
      syncTaxControls();
    }

    function incomeStreams() {
      return [
        {
          amount: numeric("finder-pension"),
          indexed: checked("finder-pension-indexed"),
          inflationRate: 0.026,
        },
        {
          amount: numeric("finder-other-income"),
          indexed: checked("finder-other-income-indexed"),
          inflationRate: 0.026,
        },
      ];
    }

    function collectUser() {
      const housingPlan = selected("finder-housing-plan");
      return {
        currentAge: numeric("finder-current-age"),
        retirementAge: numeric("finder-retirement-age"),
        horizonYears: numeric("finder-horizon"),
        household: selected("finder-household"),
        housingPlan: housingPlan,
        totalLiquidCapital: numeric("finder-liquid-capital"),
        monthlyPortfolioContribution: numeric("finder-monthly-contribution"),
        contributionInflationLinked: checked("finder-contribution-indexed"),
        expectedPortfolioReturn: numeric("finder-return") / 100,
        returnBasis: "after_fees_and_tax",
        taxMode: selectedTaxMode(),
        taxProfile: {
          dependableIncome: numeric("finder-pension") + numeric("finder-other-income"),
          portfolioWithdrawals: numeric("finder-tax-withdrawals"),
          realizedGainIntensity: selected("finder-tax-gain-intensity"),
          propertyUse: housingPlan === "rent" || element("finder-tax-property-use").disabled
            ? "none"
            : selected("finder-tax-property-use"),
          wealthBand: element("finder-tax-wealth-band").disabled
            ? "unknown"
            : selected("finder-tax-wealth-band"),
        },
        generalInflation: 0.026,
        emergencyReserveMonths: 12,
        incomeStreams: incomeStreams(),
        preferences: {
          region: selected("finder-region"),
          climate: selected("finder-climate"),
          healthcare: selected("finder-healthcare"),
        },
        maximumPropertyAllocation: numeric("finder-property-allocation"),
        purchaseMethod: selected("finder-purchase-method"),
        residency: selected("finder-buyer-residency"),
        incomeSource: selected("finder-income-source"),
        requestedLtv: numeric("finder-requested-ltv") / 100,
        annualMortgageRate: numeric("finder-mortgage-rate") / 100,
        mortgageTermYears: numeric("finder-mortgage-term"),
        mortgageTreatment: selected("finder-mortgage-treatment"),
        useBeforeRetirement: selected("finder-use-before-retirement"),
        grossRentalYield: numeric("finder-rental-yield") / 100,
        vacancyRate: numeric("finder-vacancy-rate") / 100,
        operatingCostRate: numeric("finder-operating-cost-rate") / 100,
      };
    }

    function validate(user) {
      const errors = [];
      if (!(user.retirementAge > user.currentAge)) errors.push("Retirement age must be later than current age.");
      if (user.totalLiquidCapital < 0) errors.push("Capital today cannot be negative.");
      if (user.monthlyPortfolioContribution < 0) errors.push("Monthly investing cannot be negative.");
      if (user.expectedPortfolioReturn < -0.05 || user.expectedPortfolioReturn > 0.15) {
        errors.push("Expected return must be between -5% and 15%.");
      }
      if (user.housingPlan === "buy_now" && user.maximumPropertyAllocation <= 0) {
        errors.push("Enter the maximum amount available for a property purchase.");
      }
      return errors;
    }

    function renderChart(projection) {
      const chart = element("finder-projection-bars");
      chart.innerHTML = "";
      if (!projection || !projection.annualProjection) {
        element("finder-projection-wrap").hidden = true;
        element("finder-buy-now-chart-note").hidden = false;
        return;
      }
      element("finder-projection-wrap").hidden = false;
      element("finder-buy-now-chart-note").hidden = true;
      chart.style.setProperty("--finder-chart-mobile-width", mobileChartWidth(projection.annualProjection.length) + "px");
      const maximum = Math.max.apply(null, projection.annualProjection.map(function (point) {
        return Math.max(0, Number(point.portfolio));
      }).concat([1]));
      projection.annualProjection.forEach(function (point, index) {
        const button = document.createElement("button");
        const tooltip = chartTooltip(point);
        button.type = "button";
        button.className = "finder-chart-bar";
        button.style.height = Math.max(3, Number(point.portfolio) / maximum * 100) + "%";
        button.style.animationDelay = index * 35 + "ms";
        button.setAttribute("aria-label", tooltip.accessibleLabel);
        button.dataset.heading = tooltip.heading;
        button.dataset.value = tooltip.value;
        chart.appendChild(button);
      });
    }

    function showTooltip(button) {
      element("finder-tooltip-heading").textContent = button.dataset.heading;
      element("finder-tooltip-value").textContent = button.dataset.value;
      element("finder-chart-tooltip").hidden = false;
    }

    function resultRow(item, user) {
      const propertyBits = user.housingPlan === "buy_now"
        ? '<div><dt>Property equity</dt><dd>' + money.format(item.propertyEquity) +
          '</dd></div><div><dt>Mortgage remaining</dt><dd>' + money.format(item.mortgageBalance) + "</dd></div>"
        : "";
      const rental = user.housingPlan === "buy_now" && user.useBeforeRetirement === "rental"
        ? '<div><dt>Annual property cash flow</dt><dd>' + money.format(item.netRentalCashFlow) + "</dd></div>"
        : "";
      const financing = user.housingPlan === "buy_now"
        ? '<p class="finder-financing"><strong>' + escapeHtml(item.financingStatus) + "</strong>" +
          (item.financingReason ? " — " + escapeHtml(item.financingReason) : "") + "</p>"
        : "";
      const dossierHref = safeDossierHref(item.destinationId);
      const detailHref = safeDetailHref({
        destinationId: item.destinationId,
        household: user.household,
        housingPlan: user.housingPlan,
      });
      return '<article class="finder-result"><header><div><p class="finder-tier">' +
        escapeHtml(tierLabel(item.tier)) + '</p><h3><a href="' + escapeHtml(dossierHref) +
        '" data-finder-dossier>' + escapeHtml(item.name) + "</a>" +
        '</h3><p class="finder-place">' + escapeHtml(item.country) +
        '</p></div></header><dl>' +
        '<div><dt>Projected portfolio</dt><dd>' + money.format(item.portfolioAtRetirement) + "</dd></div>" +
        '<div><dt>Retirement target</dt><dd>' + money.format(item.retirementTarget) + "</dd></div>" +
        '<div><dt>Surplus or gap</dt><dd>' + money.format(item.surplusGap) + "</dd></div>" +
        propertyBits + rental + "</dl>" + financing +
        (item.preferenceMatches.length ? '<p class="finder-matches"><strong>Preference match:</strong> ' + escapeHtml(item.preferenceMatches.join(" · ")) + "</p>" : "") +
        '<div class="finder-result-actions"><a href="' + escapeHtml(dossierHref) +
        '" data-finder-dossier>View destination dossier</a><a href="' + escapeHtml(detailHref) +
        '" data-finder-detail>Build a detailed plan</a></div>' +
        "</article>";
    }

    function renderRecommendationList() {
      const visible = recommendationsForDisplay({
        items: currentRecommendations,
        expanded: recommendationsExpanded,
      });
      element("finder-recommendations").innerHTML = visible.map(function (item) {
        return resultRow(item, currentUser);
      }).join("");
      const toggle = element("finder-show-all");
      toggle.hidden = currentRecommendations.length <= 5;
      toggle.textContent = recommendationsExpanded ? "Show the strongest five" : "View all destinations";
      toggle.setAttribute("aria-expanded", recommendationsExpanded ? "true" : "false");
    }

    function renderEvidence(items) {
      const profiles = payload.mortgageProfiles;
      const seen = new Set();
      const rows = items.slice(0, 8).map(function (item) {
        const profile = profiles[item.destinationId];
        if (!profile || seen.has(item.destinationId)) return "";
        seen.add(item.destinationId);
        const sources = (profile.sources || []).map(function (source) {
          return '<a href="' + escapeHtml(source.url) + '" rel="noopener">' + escapeHtml(source.name) + "</a>";
        }).join(", ");
        return "<li><strong>" + escapeHtml(item.name) + ":</strong> " +
          escapeHtml(item.financingStatus) + ". Evidence " + escapeHtml(profile.evidence_date || payload.asOf) +
          (sources ? " — " + sources : " — no verified lender terms yet") + ".</li>";
      }).join("");
      element("finder-financing-evidence-list").innerHTML = rows;
      element("finder-financing-evidence").hidden = rows === "";
    }

    function exclusionReason(code) {
      return {
        missing_cost_data: "Retirement cost data is incomplete.",
        buyer_access_restricted: "Foreign-buyer access is restricted.",
        financing_unverified: "No verified mortgage route is available yet.",
        no_standard_mortgage: "No standard non-resident mortgage route was identified.",
        mortgage_profile_mismatch: "Published lending terms do not match the selected residency and income profile.",
        property_finance_unavailable: "The purchase cannot be funded within the selected property allocation and lending terms.",
      }[code] || "The destination could not be evaluated under these assumptions.";
    }

    function renderExclusions(items) {
      element("finder-exclusion-list").innerHTML = items.map(function (item) {
        return "<li><strong>" + escapeHtml(item.name) + ":</strong> " +
          escapeHtml(exclusionReason(item.reasonCode)) + "</li>";
      }).join("");
      element("finder-exclusions").hidden = items.length === 0;
    }

    function render(result, user) {
      element("finder-capital-today").textContent = money.format(user.totalLiquidCapital);
      element("finder-monthly-summary").textContent = money.format(user.monthlyPortfolioContribution);
      element("finder-within-count").textContent = String(result.summary.withinReachCount);
      renderChart(result.sharedProjection);
      currentRecommendations = result.recommendations.slice(0, 12);
      currentUser = user;
      recommendationsExpanded = false;
      element("finder-result-read").textContent = resultSummaryRead({
        withinReachCount: result.summary.withinReachCount,
        recommendations: currentRecommendations,
      });
      element("finder-closest-match").textContent = currentRecommendations.length
        ? currentRecommendations[0].name
        : "—";
      renderRecommendationList();
      element("finder-excluded-summary").textContent = result.excluded.length
        ? result.excluded.length + " destinations could not be recommended under these assumptions."
        : "Every destination had enough information to evaluate.";
      renderExclusions(result.excluded);
      renderEvidence(currentRecommendations);
      results.hidden = false;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
      track("retirement_destination_finder_complete", {
        housing_plan: user.housingPlan,
        purchase_method: user.housingPlan === "buy_now" ? user.purchaseMethod : "not_applicable",
      });
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const user = collectUser();
      const errors = validate(user);
      if (errors.length) {
        errorSummary.innerHTML = "<strong>Check these fields:</strong><ul>" + errors.map(function (error) {
          return "<li>" + escapeHtml(error) + "</li>";
        }).join("") + "</ul>";
        errorSummary.hidden = false;
        errorSummary.focus();
        return;
      }
      errorSummary.hidden = true;
      try {
        const result = root.GHARetirementDestinationFinder.recommendDestinations({
          user: user,
          destinations: payload.destinations,
          retirementCosts: payload.retirementCosts,
          mortgageProfiles: payload.mortgageProfiles,
        });
        render(result, user);
      } catch (error) {
        errorSummary.textContent = error.message || "The calculation could not be completed.";
        errorSummary.hidden = false;
        errorSummary.focus();
      }
    });

    ["finder-housing-plan", "finder-purchase-method", "finder-use-before-retirement"].forEach(function (id) {
      element(id).addEventListener("change", function () {
        syncHousing();
        if (id === "finder-housing-plan") track("retirement_destination_finder_housing", { housing_plan: selected(id) });
        if (id === "finder-purchase-method" && selected(id) === "mortgage") {
          track("retirement_destination_finder_mortgage_open", { purchase_method: "mortgage" });
        }
      });
    });
    form.querySelectorAll('input[name="finder-tax-mode"]').forEach(function (control) {
      control.addEventListener("change", syncTaxControls);
    });
    element("finder-projection-bars").addEventListener("mouseover", function (event) {
      if (event.target.matches(".finder-chart-bar")) showTooltip(event.target);
    });
    element("finder-projection-bars").addEventListener("focusin", function (event) {
      if (event.target.matches(".finder-chart-bar")) showTooltip(event.target);
    });
    element("finder-recommendations").addEventListener("click", function (event) {
      if (event.target.closest("[data-finder-detail]")) track("retirement_destination_finder_detail_open");
    });
    element("finder-show-all").addEventListener("click", function () {
      recommendationsExpanded = !recommendationsExpanded;
      renderRecommendationList();
      track("retirement_destination_finder_results_toggle", { expanded: recommendationsExpanded });
    });
    syncHousing();
    track("retirement_destination_finder_open");
  }

  return {
    housingVisibility: housingVisibility,
    taxControlVisibility: taxControlVisibility,
    safeDetailHref: safeDetailHref,
    safeDossierHref: safeDossierHref,
    recommendationsForDisplay: recommendationsForDisplay,
    resultSummaryRead: resultSummaryRead,
    tierLabel: tierLabel,
    chartTooltip: chartTooltip,
    mobileChartWidth: mobileChartWidth,
    initRetirementDestinationFinder: initRetirementDestinationFinder,
  };
});
