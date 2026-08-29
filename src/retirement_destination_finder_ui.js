(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementDestinationFinderUI = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  const MONEY_CONTROL_IDS = [
    "finder-liquid-capital",
    "finder-monthly-contribution",
    "finder-property-allocation",
    "finder-pension",
    "finder-other-income",
  ];

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

  function activeMoneyControlIds(input) {
    const active = MONEY_CONTROL_IDS.filter(function (id) {
      return id !== "finder-property-allocation";
    });
    if (input.housingPlan === "buy_now") active.push("finder-property-allocation");
    return active;
  }

  function validPlanningRate(currency, ratesToUsd) {
    const rate = Number((ratesToUsd || {})[currency]);
    return Number.isFinite(rate) && rate > 0;
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

  function resultSummaryRead(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const closest = recommendations[0];
    if (!closest) return "No destinations could be evaluated under these assumptions.";
    if (Number(input.withinReachCount) > 0) {
      return Number(input.withinReachCount) + " destinations are within reach. " +
        closest.name + " is the strongest modeled match under your preferences.";
    }
    return "No destinations are within reach yet. " + closest.name +
      " is the strongest modeled match, with a gap of " + resultMoney({
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

  function finderCapitalLandscape(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const strongest = new Map(recommendations.slice(0, 3).map(function (item, index) {
      return [item.destinationId, index + 1];
    }));
    const rows = recommendations.map(function (item) {
      const target = Math.max(0, Number(item.retirementTarget) || 0);
      return {
        destinationId: item.destinationId,
        name: item.name,
        country: item.country,
        tier: item.tier,
        target: target,
        matchRank: strongest.get(item.destinationId) || null,
      };
    }).sort(function (left, right) {
      return left.target - right.target || String(left.name).localeCompare(String(right.name));
    });
    const projectedCapital = Math.max(0, Number(input.projectedCapital) || 0);
    const rawMaximum = Math.max.apply(null, rows.map(function (row) { return row.target; })
      .concat([projectedCapital, 1]));
    const roughStep = rawMaximum / 4;
    const magnitude = Math.pow(10, Math.floor(Math.log10(roughStep)));
    const normalized = roughStep / magnitude;
    const niceFactor = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 2.5 ? 2.5 :
      normalized <= 5 ? 5 : 10;
    const tickStep = niceFactor * magnitude;
    const maximum = tickStep * 4;
    return {
      maximum: maximum,
      projectedCapital: projectedCapital,
      projectedPosition: projectedCapital / maximum * 100,
      ticks: [0, 1, 2, 3, 4].map(function (index) { return tickStep * index; }),
      rows: rows.map(function (row) {
        return Object.assign({}, row, { position: row.target / maximum * 100 });
      }),
    };
  }

  function finderCapitalLandscapeLabel(input) {
    const row = input.row || {};
    const target = resultMoney({
      amountUsd: Number(row.target) || 0,
      currency: input.currency || "USD",
      ratesToUsd: input.ratesToUsd || { USD: 1 },
    });
    return String(row.name || "Destination") + ", " + String(row.country || "") +
      ". Retirement target " + target + ". " + tierLabel(row.tier) + "." +
      (row.matchRank ? " Strongest modeled match number " + row.matchRank + "." : "");
  }

  function finderCapitalLandscapeMarkup(input) {
    const model = input.model || { rows: [], ticks: [], projectedPosition: 0 };
    const currency = input.currency || "USD";
    const ratesToUsd = input.ratesToUsd || { USD: 1 };
    const capitalPosition = Math.max(0, Math.min(100, Number(model.projectedPosition) || 0));
    const axisHtml = '<span></span><span class="finder-landscape-axis-track">' +
      (model.ticks || []).map(function (tick) {
        return "<span>" + escapeHtml(resultMoney({ amountUsd: tick, currency: currency, ratesToUsd: ratesToUsd })) + "</span>";
      }).join("") + "</span><span></span>";
    const rowsHtml = (model.rows || []).map(function (row) {
      const targetPosition = Math.max(0, Math.min(100, Number(row.position) || 0));
      const label = finderCapitalLandscapeLabel({ row: row, currency: currency, ratesToUsd: ratesToUsd });
      const value = resultMoney({ amountUsd: row.target, currency: currency, ratesToUsd: ratesToUsd });
      const rank = row.matchRank
        ? '<small class="finder-landscape-rank">Match 0' + row.matchRank + "</small>"
        : "";
      return '<div role="listitem"><a class="finder-landscape-row' + (row.matchRank ? " is-match" : "") +
        '" href="' + escapeHtml(safeDossierHref(row.destinationId)) +
        '" aria-label="' + escapeHtml(label) + '" style="--capital-position:' + capitalPosition.toFixed(2) +
        "%;--target-position:" + targetPosition.toFixed(2) + '%"><span class="finder-landscape-name">' +
        escapeHtml(row.name) + "<small>" + escapeHtml(row.country) + "</small>" + rank +
        '</span><span class="finder-landscape-track" aria-hidden="true"><i class="finder-landscape-dot"></i></span>' +
        '<span class="finder-landscape-value">' + escapeHtml(value) + "</span></a></div>";
    }).join("");
    return { axisHtml: axisHtml, rowsHtml: rowsHtml, rowCount: (model.rows || []).length };
  }

  function finderProjectedCapital(input) {
    const shared = input.sharedProjection;
    if (shared && Number.isFinite(Number(shared.portfolioAtRetirement))) {
      return Math.max(0, Number(shared.portfolioAtRetirement));
    }
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    return recommendations.length ? Math.max(0, Number(recommendations[0].portfolioAtRetirement) || 0) : 0;
  }

  function finderProjectionModel(input) {
    const series = Array.isArray(input.series) ? input.series : [];
    const targetValue = Math.max(0, Number(input.targetValue) || 0);
    const maximum = Math.max.apply(null, series.map(function (point) {
      return Math.max(0, Number(point.portfolio) || 0);
    }).concat([targetValue, 1]));
    return {
      maximum: maximum,
      targetY: 258 - targetValue / maximum * 240,
      years: series.map(function (point) {
        const portfolio = Math.max(0, Number(point.portfolio) || 0);
        return {
          year: Number(point.year),
          portfolio: portfolio,
          height: portfolio / maximum * 240,
        };
      }),
    };
  }

  function finderProjectionTooltip(input) {
    const point = input.point;
    const year = Number(point.year);
    const age = Number(input.currentAge) + year;
    const heading = "Year " + year + " · age " + age;
    const value = resultMoney({
      amountUsd: Number(point.portfolio),
      currency: input.currency || "USD",
      ratesToUsd: input.ratesToUsd || { USD: 1 },
    });
    return {
      heading: heading,
      value: value,
      accessibleLabel: "Year " + year + ", age " + age + ". Projected portfolio " + value + ".",
    };
  }

  function finderProjectionAxisLabel(input) {
    const year = Number(input.year);
    const age = Number(input.currentAge) + year;
    return (year === 0 ? "Now" : "+" + year + "y") + " · age " + age;
  }

  function finderProjectionView(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const closest = recommendations[0];
    if (!closest) return null;
    const shared = input.sharedProjection && Array.isArray(input.sharedProjection.annualProjection)
      ? input.sharedProjection.annualProjection
      : [];
    const destinationSeries = Array.isArray(closest.annualProjection) ? closest.annualProjection : [];
    const buyNow = input.housingPlan === "buy_now";
    return {
      heading: buyNow ? "Projection for " + closest.name : "Projected portfolio by year",
      series: buyNow ? destinationSeries : shared,
      targetValue: Number(closest.retirementTarget),
      destinationName: closest.name,
    };
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
    const moneyControlIds = MONEY_CONTROL_IDS.slice();
    const canonicalMoneyUsd = {};
    let currentRecommendations = [];
    let currentUser = null;
    let currentResult = null;

    function element(id) { return document.getElementById(id); }
    function numeric(id) { return Number(element(id).value); }
    function checked(id) { return element(id).checked; }
    function selected(id) { return element(id).value; }
    function displayResultMoney(amountUsd) {
      return resultMoney({ amountUsd: amountUsd, currency: selectedCurrency, ratesToUsd: ratesToUsd });
    }
    function moneyNumber(id) {
      const control = element(id);
      const amount = parseMoneyInput(control.value);
      if (amount !== null && Object.prototype.hasOwnProperty.call(canonicalMoneyUsd, id)) {
        return canonicalMoneyUsd[id];
      }
      return Number(convertPlanningAmount({
        amount: amount === null ? 0 : amount,
        fromCurrency: selectedCurrency,
        toCurrency: "USD",
        ratesToUsd: ratesToUsd,
      }) || 0);
    }
    function updateCanonicalMoney(control) {
      const amount = parseMoneyInput(control.value);
      if (amount === null) return;
      const amountUsd = convertPlanningAmount({
        amount: amount,
        fromCurrency: selectedCurrency,
        toCurrency: "USD",
        ratesToUsd: ratesToUsd,
      });
      if (amountUsd !== null) canonicalMoneyUsd[control.id] = amountUsd;
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
        group.querySelectorAll("input, select, textarea").forEach(function (control) {
          control.disabled = group.hidden;
        });
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
      const invalidMoney = activeMoneyControlIds({ housingPlan: user.housingPlan }).find(function (id) {
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
      if (nextCurrency === selectedCurrency) return false;
      if (!validPlanningRate(selectedCurrency, ratesToUsd) || !validPlanningRate(nextCurrency, ratesToUsd)) {
        element("finder-currency").value = selectedCurrency;
        return false;
      }
      const previousCurrency = selectedCurrency;
      moneyControlIds.forEach(function (id) {
        const control = element(id);
        if (!control || control.value === "") return;
        const amount = parseMoneyInput(control.value);
        if (amount === null) return;
        const hasCanonical = Object.prototype.hasOwnProperty.call(canonicalMoneyUsd, id);
        const converted = convertPlanningControlAmount({
          amount: hasCanonical ? canonicalMoneyUsd[id] : amount,
          fromCurrency: hasCanonical ? "USD" : previousCurrency,
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
      return true;
    }

    function renderChart(view, user) {
      const figure = element("finder-projection-wrap");
      const barsLayer = element("finder-projection-bars");
      const fallback = element("finder-buy-now-chart-note");
      const series = view && Array.isArray(view.series)
        ? view.series
        : [];
      barsLayer.innerHTML = "";
      element("finder-chart-tooltip").hidden = true;
      if (!view || !series.length) {
        figure.hidden = true;
        fallback.hidden = false;
        return;
      }
      const model = finderProjectionModel({
        series: series,
        targetValue: view.targetValue,
      });
      const count = model.years.length;
      const left = 34;
      const baseline = 258;
      const plotWidth = 572;
      const step = count > 1 ? plotWidth / (count - 1) : plotWidth;
      const barWidth = Math.max(5, Math.min(18, step * 0.62));
      const labelEvery = Math.max(1, Math.ceil((count - 1) / 6));
      const delayStep = count > 1 ? Math.min(90, 2400 / (count - 1)) : 0;
      const bars = model.years.map(function (point, index) {
        const x = left + index * step - barWidth / 2;
        const y = baseline - point.height;
        const label = finderProjectionAxisLabel({ year: point.year, currentAge: user.currentAge });
        const yearLabel = index % labelEvery === 0 || index === count - 1
          ? '<text class="finder-chart-axis-label" x="' + (left + index * step).toFixed(2) + '" y="278" text-anchor="middle">' + label + "</text>"
          : "";
        const tooltipContent = finderProjectionTooltip({
          currentAge: user.currentAge,
          point: point,
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        });
        return '<g class="finder-chart-year" tabindex="0" role="img" data-year-index="' + index +
          '" aria-label="' + escapeHtml(tooltipContent.accessibleLabel) + '" style="--year-delay:' +
          Math.round(index * delayStep) + 'ms"><rect class="finder-chart-bar" x="' + x.toFixed(2) +
          '" y="' + y.toFixed(2) + '" width="' + barWidth.toFixed(2) + '" height="' +
          point.height.toFixed(2) + '"></rect>' + yearLabel + "</g>";
      }).join("");
      barsLayer.innerHTML = '<line class="finder-chart-axis" x1="22" y1="258" x2="618" y2="258"></line>' + bars;
      const targetLine = element("finder-chart-target");
      const targetLabel = element("finder-chart-target-label");
      targetLine.setAttribute("y1", model.targetY.toFixed(2));
      targetLine.setAttribute("y2", model.targetY.toFixed(2));
      targetLabel.setAttribute("y", Math.max(14, model.targetY - 6).toFixed(2));
      targetLabel.textContent = "Target " + displayResultMoney(view.targetValue);
      element("finder-projection-heading").textContent = view.heading;
      element("finder-projection-desc").textContent = "Annual liquid portfolio progression from age " +
        user.currentAge + " to retirement, compared with the target for " + view.destinationName + ".";
      const finalPoint = model.years[count - 1];
      element("finder-projection-caption").textContent = "At retirement: " +
        displayResultMoney(finalPoint.portfolio) + ". Target for " + view.destinationName + ": " +
        displayResultMoney(view.targetValue) + ".";
      const tooltip = element("finder-chart-tooltip");
      const groups = Array.from(barsLayer.querySelectorAll(".finder-chart-year"));
      function showTooltip(group) {
        groups.forEach(function (item) { item.classList.toggle("is-active", item === group); });
        const content = finderProjectionTooltip({
          currentAge: user.currentAge,
          point: model.years[Number(group.dataset.yearIndex)],
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        });
        element("finder-tooltip-heading").textContent = content.heading;
        element("finder-tooltip-value").textContent = content.value;
        tooltip.hidden = false;
      }
      function hideTooltip(group) {
        if (document.activeElement === group) return;
        group.classList.remove("is-active");
        tooltip.hidden = true;
      }
      groups.forEach(function (group) {
        group.addEventListener("mouseenter", function () { showTooltip(group); });
        group.addEventListener("mouseleave", function () { hideTooltip(group); });
        group.addEventListener("focus", function () { showTooltip(group); });
        group.addEventListener("blur", function () { hideTooltip(group); });
        group.addEventListener("click", function () { showTooltip(group); });
      });
      figure.hidden = false;
      fallback.hidden = true;
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
      element("finder-recommendations").innerHTML = currentRecommendations.slice(0, 3).map(function (item) {
        return resultRow(item, currentUser);
      }).join("");
    }

    function renderCapitalLandscape(result) {
      const projectedCapital = finderProjectedCapital({
        sharedProjection: result.sharedProjection,
        recommendations: currentRecommendations,
      });
      element("finder-eligible-count").textContent = String(currentRecommendations.length);
      if (!currentRecommendations.length) {
        element("finder-projected-capital").textContent = "—";
        element("finder-landscape-axis").innerHTML = "";
        element("finder-landscape-rows").innerHTML = "";
        return;
      }
      element("finder-projected-capital").textContent = displayResultMoney(projectedCapital);
      const model = finderCapitalLandscape({
        recommendations: currentRecommendations,
        projectedCapital: projectedCapital,
      });
      const markup = finderCapitalLandscapeMarkup({
        model: model,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
      element("finder-landscape-axis").innerHTML = markup.axisHtml;
      element("finder-landscape-rows").innerHTML = markup.rowsHtml;
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
      element("finder-within-count").textContent = String(result.summary.withinReachCount);
      currentRecommendations = result.recommendations.slice();
      const hasRecommendations = currentRecommendations.length > 0;
      element("finder-capital-landscape").hidden = !hasRecommendations;
      element("finder-matches-section").hidden = !hasRecommendations;
      element("finder-projection-section").hidden = !hasRecommendations;
      element("finder-empty-state").hidden = hasRecommendations;
      renderCapitalLandscape(result);
      renderChart(finderProjectionView({
        housingPlan: user.housingPlan,
        sharedProjection: result.sharedProjection,
        recommendations: currentRecommendations,
      }), user);
      element("finder-result-read").textContent = resultSummaryRead({
        withinReachCount: result.summary.withinReachCount,
        recommendations: currentRecommendations,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
      element("finder-strongest-match").textContent = currentRecommendations.length
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
      if (changePlanningCurrency(element("finder-currency").value)) {
        track("retirement_destination_finder_currency_change");
      }
    });
    moneyControlIds.forEach(function (id) {
      const control = element(id);
      updateCanonicalMoney(control);
      formatMoneyControl(control);
      control.addEventListener("input", function () {
        updateCanonicalMoney(control);
        validateMoneyControl(control);
      });
      control.addEventListener("blur", function () {
        formatMoneyControl(control);
        validateMoneyControl(control);
      });
    });
    element("finder-recommendations").addEventListener("click", function (event) {
      if (event.target.closest("[data-finder-detail]")) track("retirement_destination_finder_detail_open");
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
    activeMoneyControlIds: activeMoneyControlIds,
    safeDetailHref: safeDetailHref,
    safeDossierHref: safeDossierHref,
    resultSummaryRead: resultSummaryRead,
    tierLabel: tierLabel,
    finderCapitalLandscape: finderCapitalLandscape,
    finderCapitalLandscapeLabel: finderCapitalLandscapeLabel,
    finderCapitalLandscapeMarkup: finderCapitalLandscapeMarkup,
    finderProjectedCapital: finderProjectedCapital,
    finderProjectionModel: finderProjectionModel,
    finderProjectionTooltip: finderProjectionTooltip,
    finderProjectionAxisLabel: finderProjectionAxisLabel,
    finderProjectionView: finderProjectionView,
    initRetirementDestinationFinder: initRetirementDestinationFinder,
  };
});
