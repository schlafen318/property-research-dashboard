(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementDestinationFinderUI = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  function convertPlanningAmount(input) {
    const rates = input.ratesToUsd || { USD: 1 };
    const fromRate = Number(rates[input.fromCurrency]);
    const toRate = Number(rates[input.toCurrency]);
    if (input.amount === null || input.amount === undefined || input.amount === "") return null;
    const amount = Number(input.amount);
    if (!Number.isFinite(amount) || !(fromRate > 0) || !(toRate > 0)) return null;
    return amount * fromRate / toRate;
  }

  function formatPlanningMoney(input) {
    const currency = input.currency || "USD";
    const converted = convertPlanningAmount({
      amount: input.amountUsd,
      fromCurrency: "USD",
      toCurrency: currency,
      ratesToUsd: input.ratesToUsd || { USD: 1 },
    });
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(converted === null ? 0 : converted);
  }

  function resultMoney(input) {
    return formatPlanningMoney(input);
  }

  function convertPlanningControlAmount(input) {
    const converted = convertPlanningAmount(input);
    if (converted === null) return null;
    const step = Number(input.step);
    if (!(step > 0)) return Math.round(converted);
    return Math.round(converted / step) * step;
  }

  function parseMoneyInput(value) {
    const normalized = String(value === null || value === undefined ? "" : value)
      .trim()
      .replace(/,/g, "");
    if (!/^\d+(?:\.\d+)?$/.test(normalized)) return null;
    const amount = Number(normalized);
    return Number.isFinite(amount) ? amount : null;
  }

  function formatMoneyInputValue(value) {
    const amount = typeof value === "number" ? value : parseMoneyInput(value);
    if (!Number.isFinite(amount)) return "";
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(amount);
  }

  function isInvalidMoneyInput(input) {
    const amount = parseMoneyInput(input.value);
    if (amount === null) return true;
    const minimum = input.min === "" || input.min === null || input.min === undefined
      ? null
      : Number(input.min);
    if (minimum !== null && amount < minimum) return true;
    const step = Number(input.step);
    if (!(step > 0)) return false;
    const base = minimum === null ? 0 : minimum;
    const steps = (amount - base) / step;
    return Math.abs(steps - Math.round(steps)) > 1e-9;
  }

  function housingVisibility(input) {
    const buyNow = input.housingPlan === "buy_now";
    return {
      buyNow: buyNow,
      mortgage: buyNow && ["mortgage", "not_sure"].includes(input.purchaseMethod),
      rental: buyNow && input.useBeforeRetirement === "rental",
      buyAtRetirement: input.housingPlan === "buy_retirement",
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
      " is the closest modeled match, with a gap of " + resultMoney({
        amountUsd: Math.abs(Number(closest.surplusGap)),
        currency: input.currency || "USD",
        ratesToUsd: input.ratesToUsd || { USD: 1 },
      }) + ".";
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
    const value = resultMoney({
      amountUsd: Number(point.portfolio),
      currency: point.currency || "USD",
      ratesToUsd: point.ratesToUsd || { USD: 1 },
    });
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
    const currencyConfig = payload.planning_currencies || { rates_to_usd: { USD: 1 } };
    const ratesToUsd = currencyConfig.rates_to_usd || { USD: 1 };
    let selectedCurrency = "USD";
    const moneyControlIds = [
      "finder-liquid-capital",
      "finder-monthly-contribution",
      "finder-property-allocation",
      "finder-pension",
      "finder-other-income",
    ];
    let currentRecommendations = [];
    let currentUser = null;
    let currentResult = null;
    let recommendationsExpanded = false;

    function element(id) { return document.getElementById(id); }
    function numeric(id) { return Number(element(id).value); }
    function checked(id) { return element(id).checked; }
    function selected(id) { return element(id).value; }
    function displayResultMoney(amountUsd) {
      return resultMoney({ amountUsd: amountUsd, currency: selectedCurrency, ratesToUsd: ratesToUsd });
    }
    function moneyNumber(id) {
      const amount = parseMoneyInput(element(id).value);
      return Number(convertPlanningAmount({
        amount: amount === null ? 0 : amount,
        fromCurrency: selectedCurrency,
        toCurrency: "USD",
        ratesToUsd: ratesToUsd,
      }) || 0);
    }
    function formatMoneyControl(control) {
      if (!control || control.value === "") return;
      const amount = parseMoneyInput(control.value);
      if (amount !== null) control.value = formatMoneyInputValue(amount);
    }
    function validateMoneyControl(control) {
      const invalid = isInvalidMoneyInput({ value: control.value, min: control.min, step: control.step });
      control.setCustomValidity(invalid ? "Enter a valid amount." : "");
      if (invalid) control.setAttribute("aria-invalid", "true");
      else control.removeAttribute("aria-invalid");
      return invalid;
    }
    function track(name, fields) {
      if (root.GHA && typeof root.GHA.track === "function") root.GHA.track(name, fields || {});
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
    }

    function incomeStreams() {
      return [
        {
          amount: moneyNumber("finder-pension") * 12,
          indexed: checked("finder-pension-indexed"),
          inflationRate: 0.026,
        },
        {
          amount: moneyNumber("finder-other-income") * 12,
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
        totalLiquidCapital: moneyNumber("finder-liquid-capital"),
        monthlyPortfolioContribution: moneyNumber("finder-monthly-contribution"),
        contributionInflationLinked: checked("finder-contribution-indexed"),
        expectedPortfolioReturn: numeric("finder-return") / 100,
        generalInflation: 0.026,
        emergencyReserveMonths: 12,
        incomeStreams: incomeStreams(),
        preferences: {
          region: selected("finder-region"),
          climate: selected("finder-climate"),
          healthcare: selected("finder-healthcare"),
        },
        maximumPropertyAllocation: moneyNumber("finder-property-allocation"),
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
      const invalidMoney = moneyControlIds.find(function (id) {
        return validateMoneyControl(element(id));
      });
      if (invalidMoney) errors.push("Enter a valid amount in the highlighted money field.");
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

    function changePlanningCurrency(nextCurrency) {
      if (!ratesToUsd[nextCurrency] || nextCurrency === selectedCurrency) return;
      const previousCurrency = selectedCurrency;
      moneyControlIds.forEach(function (id) {
        const control = element(id);
        if (!control || control.value === "") return;
        const amount = parseMoneyInput(control.value);
        if (amount === null) return;
        const converted = convertPlanningControlAmount({
          amount: amount,
          fromCurrency: previousCurrency,
          toCurrency: nextCurrency,
          ratesToUsd: ratesToUsd,
          step: control.step,
        });
        if (converted !== null) {
          control.value = formatMoneyInputValue(converted);
          validateMoneyControl(control);
        }
      });
      selectedCurrency = nextCurrency;
      renderCurrentResults();
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
        const tooltip = chartTooltip({
          year: point.year,
          portfolio: point.portfolio,
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        });
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
        ? '<div><dt>Property equity</dt><dd>' + displayResultMoney(item.propertyEquity) +
          '</dd></div><div><dt>Mortgage remaining</dt><dd>' + displayResultMoney(item.mortgageBalance) + "</dd></div>"
        : "";
      const rental = user.housingPlan === "buy_now" && user.useBeforeRetirement === "rental"
        ? '<div><dt>Annual property cash flow</dt><dd>' + displayResultMoney(item.netRentalCashFlow) + "</dd></div>"
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
        '<div><dt>Projected portfolio</dt><dd>' + displayResultMoney(item.portfolioAtRetirement) + "</dd></div>" +
        '<div><dt>Retirement target</dt><dd>' + displayResultMoney(item.retirementTarget) + "</dd></div>" +
        '<div><dt>Surplus or gap</dt><dd>' + displayResultMoney(item.surplusGap) + "</dd></div>" +
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

    function renderCurrentResults() {
      if (!currentResult || !currentUser) return;
      const result = currentResult;
      const user = currentUser;
      element("finder-capital-today").textContent = displayResultMoney(user.totalLiquidCapital);
      element("finder-monthly-summary").textContent = displayResultMoney(user.monthlyPortfolioContribution);
      element("finder-within-count").textContent = String(result.summary.withinReachCount);
      renderChart(result.sharedProjection);
      currentRecommendations = result.recommendations.slice(0, 12);
      element("finder-result-read").textContent = resultSummaryRead({
        withinReachCount: result.summary.withinReachCount,
        recommendations: currentRecommendations,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
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
    }

    function render(result, user) {
      currentResult = result;
      currentUser = user;
      recommendationsExpanded = false;
      renderCurrentResults();
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
    element("finder-currency").value = selectedCurrency;
    element("finder-currency").addEventListener("change", function () {
      changePlanningCurrency(element("finder-currency").value);
      track("retirement_destination_finder_currency_change");
    });
    moneyControlIds.forEach(function (id) {
      const control = element(id);
      formatMoneyControl(control);
      control.addEventListener("input", function () { validateMoneyControl(control); });
      control.addEventListener("blur", function () {
        formatMoneyControl(control);
        validateMoneyControl(control);
      });
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
    convertPlanningAmount: convertPlanningAmount,
    convertPlanningControlAmount: convertPlanningControlAmount,
    parseMoneyInput: parseMoneyInput,
    formatMoneyInputValue: formatMoneyInputValue,
    formatPlanningMoney: formatPlanningMoney,
    resultMoney: resultMoney,
    housingVisibility: housingVisibility,
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
