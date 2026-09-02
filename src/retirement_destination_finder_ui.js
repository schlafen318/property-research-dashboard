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

  function compactResultMoney(input) {
    const currency = input.currency || "USD";
    const converted = convertPlanningAmount({
      amount: input.amountUsd,
      fromCurrency: "USD",
      toCurrency: currency,
      ratesToUsd: input.ratesToUsd || { USD: 1 },
    });
    const amount = Math.max(0, converted === null ? 0 : converted);
    const divisor = amount >= 999_500 ? 1_000_000 : amount >= 1_000 ? 1_000 : 1;
    const suffix = divisor === 1_000_000 ? "m" : divisor === 1_000 ? "k" : "";
    const value = new Intl.NumberFormat("en-US", {
      maximumFractionDigits: divisor === 1_000_000 ? 2 : 0,
    }).format(amount / divisor);
    const symbol = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).formatToParts(0).filter(function (part) {
      return part.type === "currency";
    }).map(function (part) {
      return part.value;
    }).join("");
    return symbol + (symbol.length > 1 ? "\u00a0" : "") + value + suffix;
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

  function taxResultPresentation(item) {
    if (item.taxStatus !== "user_after_tax") return null;
    return {
      targetLabel: "After-tax target",
      note: "Uses your after-tax income and return; no destination tax estimate was added.",
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

  function calculatorHrefsForResults(input) {
    const recommendations = Array.isArray(input && input.recommendations) ? input.recommendations : [];
    const user = input && input.user || {};
    return recommendations.map(function (item) {
      return safeDetailHref({
        destinationId: item.destinationId,
        household: user.household,
        housingPlan: user.housingPlan,
      });
    });
  }

  function safeDossierHref(destinationId) {
    const slug = /^[a-z0-9-]+$/.test(String(destinationId || "")) ? String(destinationId) : "";
    return "/destinations/" + (slug ? encodeURIComponent(slug) + "/" : "");
  }

  function resultSummaryRead(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const closest = recommendations[0];
    if (!closest) return "No destinations match this plan yet.";
    if (closest.tier === "conditional") {
      return "Affordability is conditional where current destination tax evidence is unavailable.";
    }
    if (Number(input.withinReachCount) > 0) {
      return "Your plan puts " + Number(input.withinReachCount) + " destinations within reach. " +
        closest.name + " is your strongest overall match.";
    }
    return "No destinations are within reach yet. " + closest.name +
      " comes closest, with a gap of " + resultMoney({
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
      conditional: "Conditional",
    }[value] || "Not classified";
  }

  function finderMatchExplanation(input) {
    const item = input.item || {};
    const gap = Number(item.surplusGap) || 0;
    const currency = input.currency || "USD";
    const ratesToUsd = input.ratesToUsd || { USD: 1 };
    let affordability = tierLabel(item.tier) + ".";
    if (gap === 0) {
      affordability = "Within reach at the required capital.";
    } else if (gap > 0) {
      affordability = "Within reach with " + resultMoney({
        amountUsd: gap,
        currency: currency,
        ratesToUsd: ratesToUsd,
      }) + " remaining.";
    } else {
      affordability = tierLabel(item.tier) + ", with a " + resultMoney({
          amountUsd: Math.abs(gap),
          currency: currency,
          ratesToUsd: ratesToUsd,
        }) + " gap.";
    }
    const matches = Array.isArray(item.preferenceMatches) ? item.preferenceMatches : [];
    const labels = {
      "Preferred region": "preferred region",
      "Preferred setting": "preferred setting",
      "Stronger healthcare signal": "healthcare priorities",
      "Long-stay suitability": "long-stay priorities",
    };
    const preference = matches.length
      ? " Matches your " + matches.map(function (match) { return labels[match] || String(match).toLowerCase(); }).join(" and ") + "."
      : "";
    const housing = {
      rent: "Renting keeps more capital available.",
      own: "Existing ownership keeps acquisition costs outside this estimate.",
      buy_retirement: "The required capital includes the retirement home purchase.",
      buy_now: "The estimate reflects the selected purchase and financing plan.",
    }[input.housingPlan || "rent"];
    return affordability + preference + " " + housing;
  }

  function comparisonSelection(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const byId = new Map(recommendations.map(function (item) { return [item.destinationId, item]; }));
    const selected = [];
    (Array.isArray(input.selectedIds) ? input.selectedIds : []).forEach(function (id) {
      if (byId.has(id) && !selected.includes(id) && selected.length < 3) selected.push(id);
    });
    recommendations.forEach(function (item) {
      if (!selected.includes(item.destinationId) && selected.length < Math.min(3, recommendations.length)) {
        selected.push(item.destinationId);
      }
    });
    return selected.map(function (id) { return byId.get(id); });
  }

  function replaceComparisonDestination(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const allowed = new Set(recommendations.map(function (item) { return item.destinationId; }));
    const ids = comparisonSelection(input).map(function (item) { return item.destinationId; });
    const position = Number(input.position);
    const nextId = String(input.destinationId || "");
    if (!Number.isInteger(position) || position < 0 || position >= ids.length || !allowed.has(nextId)) return ids;
    if (ids.includes(nextId) && ids[position] !== nextId) return ids;
    ids[position] = nextId;
    return ids;
  }

  function comparisonMarkup(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const selected = comparisonSelection(input);
    const currency = input.currency || "USD";
    const ratesToUsd = input.ratesToUsd || { USD: 1 };
    function money(value) {
      if (value === null || value === undefined || !Number.isFinite(Number(value))) return "Unavailable";
      return resultMoney({ amountUsd: Number(value) || 0, currency: currency, ratesToUsd: ratesToUsd });
    }
    function options(position, selectedId) {
      const occupied = new Set(selected.map(function (item) { return item.destinationId; }));
      return recommendations.map(function (item) {
        const disabled = occupied.has(item.destinationId) && item.destinationId !== selectedId;
        return '<option value="' + escapeHtml(item.destinationId) + '"' +
          (item.destinationId === selectedId ? " selected" : "") + (disabled ? " disabled" : "") + ">" +
          escapeHtml(item.name) + "</option>";
      }).join("");
    }
    function cell(item, value) { return "<td>" + value(item) + "</td>"; }
    const headings = selected.map(function (item, index) {
      return '<th scope="col">' + escapeHtml(item.name) + '<select data-comparison-position="' + index +
        '" aria-label="Replace ' + escapeHtml(item.name) + '">' + options(index, item.destinationId) + "</select></th>";
    }).join("");
    const rowDefinitions = [
      ["Required capital", function (item) { return escapeHtml(money(item.retirementTarget)); }],
      ["Gap versus projected capital", function (item) { return escapeHtml(money(item.surplusGap)); }],
      ["Financial tier", function (item) { return escapeHtml(tierLabel(item.tier)); }],
      ["Monthly retirement cost", function (item) { return escapeHtml(money(item.monthlyRetirementCost)); }],
      ["Housing assumption", function () { return escapeHtml({ rent: "Rent", own: "Already own", buy_now: "Buy now", buy_retirement: "Buy at retirement" }[input.housingPlan] || "Rent"); }],
      ["Preference alignment", function (item) { return escapeHtml((item.preferenceMatches || []).join(" · ") || "No additional preference match"); }],
      ["Guides", function (item) {
        const country = item.countryGuideHref
          ? '<a href="' + escapeHtml(item.countryGuideHref) + '">Country guide</a>'
          : "";
        return '<span class="finder-comparison-links"><a href="' + escapeHtml(safeDossierHref(item.destinationId)) +
          '">Destination guide</a>' + country + '<a href="' + escapeHtml(safeDetailHref({
            destinationId: item.destinationId,
            household: input.household,
            housingPlan: input.housingPlan,
          })) + '">Detailed plan</a></span>';
      }],
    ];
    const rows = rowDefinitions.map(function (row) {
      return '<tr><th scope="row">' + row[0] + "</th>" + selected.map(function (item) {
        return cell(item, row[1]);
      }).join("") + "</tr>";
    }).join("");
    const mobile = selected.map(function (item, index) {
      const metrics = rowDefinitions.map(function (row) {
        return "<div><dt>" + row[0] + "</dt><dd>" + row[1](item) + "</dd></div>";
      }).join("");
      return '<article><h4>' + escapeHtml(item.name) + '</h4><select data-comparison-position="' + index +
        '" aria-label="Replace ' + escapeHtml(item.name) + '">' + options(index, item.destinationId) +
        "</select><dl>" + metrics + "</dl></article>";
    }).join("");
    return '<div class="finder-comparison-scroll"><table class="finder-comparison-table"><caption>Compare recommended retirement destinations</caption><thead><tr><th></th>' +
      headings + "</tr></thead><tbody>" + rows + '</tbody></table></div><div class="finder-comparison-mobile">' + mobile + "</div>";
  }

  function finderCapitalLandscape(input) {
    const recommendations = Array.isArray(input.recommendations) ? input.recommendations : [];
    const strongest = new Map(recommendations.slice(0, 3).map(function (item, index) {
      return [item.destinationId, index + 1];
    }));
    const rows = recommendations.filter(function (item) {
      return item.retirementTarget !== null && Number.isFinite(Number(item.retirementTarget));
    }).map(function (item) {
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
    const projectedCapital = Math.max(0, Number(input.projectedCapital) || 0);
    const difference = (Number(row.target) || 0) - projectedCapital;
    const target = resultMoney({
      amountUsd: Number(row.target) || 0,
      currency: input.currency || "USD",
      ratesToUsd: input.ratesToUsd || { USD: 1 },
    });
    const differenceText = difference === 0
      ? "Matches projected capital."
      : resultMoney({
        amountUsd: Math.abs(difference),
        currency: input.currency || "USD",
        ratesToUsd: input.ratesToUsd || { USD: 1 },
      }) + (difference < 0 ? " under projected capital." : " over projected capital.");
    return String(row.name || "Destination") + ", " + String(row.country || "") +
      ". Required capital " + target + ". " + differenceText + " " + tierLabel(row.tier) + "." +
      (row.matchRank ? " Recommended match number " + row.matchRank + "." : "");
  }

  function finderCapitalLandscapeMarkup(input) {
    const model = input.model || { rows: [], ticks: [], projectedPosition: 0 };
    const currency = input.currency || "USD";
    const ratesToUsd = input.ratesToUsd || { USD: 1 };
    const capitalPosition = Math.max(0, Math.min(100, Number(model.projectedPosition) || 0));
    const zero = compactResultMoney({ amountUsd: 0, currency: currency, ratesToUsd: ratesToUsd });
    const axisHtml = "<span></span><span></span><span>Capital needed</span>";
    const rankLabels = {
      1: "Strongest match",
      2: "Second match",
      3: "Third match",
    };
    const rowsHtml = (model.rows || []).map(function (row, index) {
      const targetPosition = Math.max(0, Math.min(100, Number(row.position) || 0));
      const difference = (Number(row.target) || 0) - (Number(model.projectedCapital) || 0);
      const state = difference === 0 ? "is-on-target" : difference < 0 ? "is-within" : "is-over";
      const label = finderCapitalLandscapeLabel({
        row: row,
        projectedCapital: model.projectedCapital,
        currency: currency,
        ratesToUsd: ratesToUsd,
      });
      const required = compactResultMoney({ amountUsd: row.target, currency: currency, ratesToUsd: ratesToUsd }) + " needed";
      const buffer = difference === 0
        ? "Matches your plan"
        : compactResultMoney({
          amountUsd: Math.abs(difference),
          currency: currency,
          ratesToUsd: ratesToUsd,
        }) + (difference < 0 ? " remaining" : " above your plan");
      const rank = row.matchRank
        ? '<small class="finder-landscape-rank">' + rankLabels[row.matchRank] + "</small>"
        : "";
      return '<div class="finder-landscape-item" role="listitem"><a class="finder-landscape-row' + (row.matchRank ? " is-match" : "") + " " + state +
        '" href="' + escapeHtml(safeDossierHref(row.destinationId)) +
        '" data-finder-destination data-destination-id="' + escapeHtml(row.destinationId) +
        '" data-surface="cost_landscape" data-cost-rank="' + (index + 1) +
        '" data-match-rank="' + (row.matchRank || "") + '" data-tier="' + escapeHtml(row.tier) +
        '" data-action="dossier"' +
        ' aria-label="' + escapeHtml(label) + '" style="--capital-position:' + capitalPosition.toFixed(2) +
        "%;--target-position:" + targetPosition.toFixed(2) + '%"><span class="finder-landscape-name">' +
        escapeHtml(row.name) + "<small>" + escapeHtml(row.country) + "</small>" + rank +
        '</span><span class="finder-landscape-track" aria-hidden="true"><i class="finder-landscape-fill"></i>' +
        '<i class="finder-landscape-cost-dot"></i><i class="finder-landscape-plan-marker"></i>' +
        '<span class="finder-landscape-scale-zero">' + escapeHtml(zero) + '</span><span class="finder-landscape-scale-plan">Your plan</span></span>' +
        '<span class="finder-landscape-value"><span class="finder-landscape-required">' + escapeHtml(required) +
        '</span><small class="finder-landscape-buffer">' + escapeHtml(buffer) + "</small></span></a></div>";
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
    const closest = recommendations.find(function (item) {
      return item.retirementTarget !== null && Number.isFinite(Number(item.retirementTarget));
    });
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
    let comparisonIds = [];
    let sharedView = false;
    let comparisonOpened = false;
    let wizardStepIndex = 0;
    let wizardView = "editing";
    const allWizardSectionIds = [
      "finder-profile",
      "finder-current-resources",
      "finder-housing",
      "finder-financing",
      "finder-before-retirement",
      "finder-retirement-income",
      "finder-tax-planning",
      "finder-preferences",
    ];
    const wizardMedia = typeof root.matchMedia === "function"
      ? root.matchMedia("(max-width: 760px) and (orientation: portrait)")
      : { matches: false };

    function element(id) { return document.getElementById(id); }
    function numeric(id) { return Number(element(id).value); }
    function checked(id) { return element(id).checked; }
    function selected(id) { return element(id).value; }
    function selectedTaxMode() {
      const control = Array.from(form.querySelectorAll('input[name="finder-tax-mode"]')).find(function (item) {
        return item.checked;
      });
      return control ? control.value : "destination_estimate";
    }
    function syncTaxControls() {
      const visibility = taxControlVisibility({ taxMode: selectedTaxMode() });
      element("finder-tax-estimate-fields").hidden = !visibility.estimate;
      element("finder-tax-after-tax-note").hidden = !visibility.afterTax;
    }
    function activeWizardSectionIds() {
      const sectionIds = ["finder-profile", "finder-current-resources", "finder-housing"];
      if (selected("finder-housing-plan") === "buy_now") {
        if (selected("finder-purchase-method") === "mortgage") sectionIds.push("finder-financing");
        sectionIds.push("finder-before-retirement");
      }
      sectionIds.push("finder-retirement-income", "finder-preferences");
      return sectionIds;
    }
    function selectedSettings() {
      return Array.from(document.querySelectorAll('[name="finder-setting"]')).filter(function (control) {
        return control.checked;
      }).map(function (control) {
        return control.value;
      });
    }
    function titleCaseFilter(value) {
      return String(value || "").replace(/-/g, " ").replace(/\b\w/g, function (letter) {
        return letter.toUpperCase();
      });
    }
    function settingLabel(value) {
      const normalized = String(value || "").toLowerCase();
      if (normalized === "coastorisland") return "Coast or island";
      if (normalized === "water") return "Water setting (legacy)";
      return titleCaseFilter(value);
    }
    function activeDestinationFilters(preferences) {
      const filters = [];
      const region = preferences && preferences.region;
      if (region && String(region).toLowerCase() !== "any") filters.push(titleCaseFilter(region));
      (preferences && Array.isArray(preferences.settings) ? preferences.settings : []).forEach(function (setting) {
        filters.push(settingLabel(setting));
      });
      return filters;
    }
    function sentenceList(values) {
      if (values.length < 2) return values.join("");
      if (values.length === 2) return values.join(" and ");
      return values.slice(0, -1).join(", ") + ", and " + values[values.length - 1];
    }
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

    function showFormErrors(errors) {
      if (!errors.length) {
        errorSummary.hidden = true;
        return;
      }
      errorSummary.innerHTML = "<strong>Check the highlighted details:</strong><ul>" + errors.map(function (error) {
        return "<li>" + escapeHtml(error) + "</li>";
      }).join("") + "</ul>";
      errorSummary.hidden = false;
      errorSummary.focus();
    }

    function wizardStepErrors(stepIndex) {
      const errors = [];
      const sectionIds = activeWizardSectionIds();
      const stepId = sectionIds[stepIndex];
      const invalidMoneyIds = stepId === "finder-current-resources"
        ? ["finder-liquid-capital", "finder-monthly-contribution"]
        : stepId === "finder-housing" && selected("finder-housing-plan") === "buy_now"
          ? ["finder-property-allocation"]
          : stepId === "finder-retirement-income"
            ? ["finder-pension", "finder-other-income"]
            : [];
      if (invalidMoneyIds.some(function (id) { return validateMoneyControl(element(id)); })) {
        errors.push("Enter a valid amount in the highlighted field.");
      }
      if (stepId === "finder-profile") {
        const currentAge = numeric("finder-current-age");
        const retirementAge = numeric("finder-retirement-age");
        const horizonYears = numeric("finder-horizon");
        if (!Number.isFinite(currentAge) || currentAge < 18 || currentAge > 90) {
          errors.push("Enter a current age between 18 and 90.");
        } else if (!Number.isFinite(retirementAge) || retirementAge <= currentAge || retirementAge > 100) {
          errors.push("Retirement age must be later than your current age.");
        }
        if (!Number.isFinite(horizonYears) || horizonYears < 1 || horizonYears > 60) {
          errors.push("Enter between 1 and 60 years for retirement.");
        }
      }
      if (stepId === "finder-current-resources") {
        const expectedReturn = numeric("finder-return");
        if (!Number.isFinite(expectedReturn) || expectedReturn < -5 || expectedReturn > 15) {
          errors.push("Expected return must be between -5% and 15%.");
        }
      }
      if (stepId === "finder-housing" && selected("finder-housing-plan") === "buy_now" &&
          moneyNumber("finder-property-allocation") <= 0) {
        errors.push("Enter your property purchase budget.");
      }
      const activeSection = element(stepId);
      let invalidControl = null;
      Array.from(activeSection.querySelectorAll("input, select, textarea")).forEach(function (control) {
        if (control.disabled || typeof control.checkValidity !== "function") return;
        if (control.checkValidity()) {
          control.removeAttribute("aria-invalid");
        } else if (!invalidControl) {
          invalidControl = control;
        }
      });
      if (invalidControl) {
        invalidControl.setAttribute("aria-invalid", "true");
        if (typeof invalidControl.reportValidity === "function") invalidControl.reportValidity();
        if (typeof invalidControl.focus === "function") invalidControl.focus();
        errors.push("Correct the highlighted field to continue.");
      }
      return errors;
    }

    function reviewMoney(amountUsd, controlId) {
      const converted = convertPlanningControlAmount({
        amount: amountUsd,
        fromCurrency: "USD",
        toCurrency: selectedCurrency,
        ratesToUsd: ratesToUsd,
        step: element(controlId).step,
      });
      return selectedCurrency + " " + formatMoneyInputValue(converted);
    }

    function reviewPercent(value) {
      return String(Math.round(Number(value || 0) * 1000) / 10);
    }

    function updateReview(user) {
      const household = user.household === "couple" ? "Couple" : "Single";
      const housingLabels = {
        rent: "Rent a home",
        buy_now: "Buy a home now",
        buy_retirement: "Buy a home at retirement",
        own: "Already own my retirement home",
      };
      const settings = (user.preferences.settings || []).map(settingLabel);
      const region = user.preferences.region === "any"
        ? "Any region"
        : titleCaseFilter(user.preferences.region);
      const contributionIndexing = user.contributionInflationLinked
        ? ", inflation-linked"
        : "";
      const housing = user.housingPlan;
      const housingParts = [housingLabels[housing] || "—"];
      if (housing === "buy_now") {
        housingParts.push(reviewMoney(user.maximumPropertyAllocation, "finder-property-allocation"));
        const purchaseMethod = user.purchaseMethod;
        if (purchaseMethod === "mortgage") {
          housingParts.push(
            "Mortgage: " + reviewPercent(user.requestedLtv) + "% LTV, " +
            reviewPercent(user.annualMortgageRate) + "%, " + user.mortgageTermYears + " years"
          );
          const residencyLabels = {
            non_resident: "Non-resident",
            resident: "Resident",
            eu_national: "EU national",
            non_resident_with_purchase_permit: "Non-resident with purchase permission",
          };
          housingParts.push(residencyLabels[user.residency] || "Buyer status not set");
          housingParts.push(user.mortgageTreatment === "continue"
            ? "Continue repayments in retirement"
            : "Pay off at retirement");
        } else {
          housingParts.push(purchaseMethod === "cash" ? "Cash purchase" : "Financing not decided");
        }
        if (user.useBeforeRetirement === "rental") {
          housingParts.push("Rent before retirement");
        } else {
          housingParts.push("Personal use before retirement");
        }
      }
      const incomeParts = [];
      const pension = user.incomeStreams[0] || {};
      const otherIncome = user.incomeStreams[1] || {};
      if (Number(pension.amount) > 0) {
        incomeParts.push(
          reviewMoney(Number(pension.amount) / 12, "finder-pension") + "/month pension" +
          (pension.indexed ? ", inflation-linked" : "")
        );
      }
      if (Number(otherIncome.amount) > 0) {
        incomeParts.push(
          reviewMoney(Number(otherIncome.amount) / 12, "finder-other-income") + "/month other income" +
          (otherIncome.indexed ? ", inflation-linked" : "")
        );
      }
      element("finder-review-retirement").textContent =
        "Age " + user.currentAge + " now · retire at " + user.retirementAge + " · " +
        household + " · " + user.horizonYears + " years";
      element("finder-review-capital").textContent =
        reviewMoney(user.totalLiquidCapital, "finder-liquid-capital") + " today · " +
        reviewMoney(user.monthlyPortfolioContribution, "finder-monthly-contribution") + "/month" +
        contributionIndexing + " · " + reviewPercent(user.expectedPortfolioReturn) + "% return";
      element("finder-review-housing").textContent = housingParts.join(" · ");
      element("finder-review-income").textContent = incomeParts.length
        ? incomeParts.join(" · ")
        : "No continuing income";
      element("finder-review-preferences").textContent =
        region + " · " + (settings.length ? sentenceList(settings) : "Any setting") +
        " · Healthcare: " + (user.preferences.healthcare === "high" ? "top priority" : "important");
    }

    function updateWizardStep(options) {
      const active = Boolean(wizardMedia.matches);
      const progress = element("finder-wizard-progress");
      const actions = element("finder-wizard-actions");
      const sectionIds = activeWizardSectionIds();
      const activeId = sectionIds[wizardStepIndex] || sectionIds[sectionIds.length - 1];
      if (wizardStepIndex >= sectionIds.length) wizardStepIndex = sectionIds.length - 1;
      const sections = sectionIds.map(element);
      progress.hidden = !active;
      actions.hidden = !active;
      allWizardSectionIds.forEach(function (sectionId) {
        const section = element(sectionId);
        const conditional = sectionId === "finder-financing" || sectionId === "finder-before-retirement";
        section.hidden = active ? sectionId !== activeId : conditional && sectionIds.indexOf(sectionId) === -1;
      });
      element("finder-tax-planning").hidden = active ? activeId !== "finder-retirement-income" : false;
      if (!active) return;
      const stepNumber = wizardStepIndex + 1;
      element("finder-wizard-step").textContent = "Step " + stepNumber + " of " + sections.length;
      const progressbar = element("finder-wizard-progressbar");
      progressbar.setAttribute("aria-valuenow", String(stepNumber));
      progressbar.setAttribute("aria-valuemax", String(sections.length));
      progressbar.style.setProperty("--finder-progress", String((stepNumber / sections.length) * 100) + "%");
      element("finder-wizard-back").hidden = wizardStepIndex === 0;
      element("finder-wizard-next").textContent = wizardStepIndex === sections.length - 1
        ? "See my destinations"
        : "Continue";
      element("finder-wizard-next").disabled = activeId === "finder-housing" &&
        selected("finder-housing-plan") === "own";
      document.body.classList.toggle("finder-wizard-editing", wizardView === "editing");
      if (options && options.focus) {
        sections[wizardStepIndex].focus({ preventScroll: true });
        sections[wizardStepIndex].scrollTop = 0;
      }
    }

    function advanceWizard() {
      const sectionIds = activeWizardSectionIds();
      const errors = wizardStepErrors(wizardStepIndex);
      showFormErrors(errors);
      if (errors.length) return;
      if (wizardStepIndex === sectionIds.length - 1) {
        form.requestSubmit();
        return;
      }
      wizardStepIndex += 1;
      updateWizardStep({ focus: true });
    }

    function returnToWizard() {
      wizardView = "editing";
      form.hidden = false;
      results.hidden = true;
      element("finder-adjust-plan").hidden = true;
      wizardStepIndex = activeWizardSectionIds().length - 1;
      updateWizardStep({ focus: true });
    }

    function syncWizardMode() {
      const active = Boolean(wizardMedia.matches);
      if (!active) {
        document.body.classList.remove("finder-wizard-editing");
        form.hidden = false;
        if (currentResult) results.hidden = wizardView === "editing";
        element("finder-adjust-plan").hidden = true;
      } else if (currentResult && wizardView !== "editing") {
        document.body.classList.remove("finder-wizard-editing");
        form.hidden = true;
        results.hidden = false;
        element("finder-adjust-plan").hidden = wizardView === "shared";
      } else {
        form.hidden = false;
        if (currentResult) results.hidden = true;
        element("finder-adjust-plan").hidden = true;
      }
      updateWizardStep();
    }

    function finderScenarioValue(search) {
      if (root.__ghaFinderScenario) return String(root.__ghaFinderScenario);
      const match = String(search || "").match(/(?:^|[?&])scenario=([^&]+)/);
      if (!match) return "";
      try { return decodeURIComponent(match[1]); } catch (error) { return ""; }
    }

    function destinationDetails(destinationId, user) {
      const destination = (payload.destinations || []).find(function (item) { return item.id === destinationId; });
      const cost = (payload.retirementCosts || []).find(function (item) { return item.destination_id === destinationId; });
      const profile = cost && cost.profiles && cost.profiles[user.household];
      const housing = profile && user.housingPlan === "rent" ? profile.annual_rent_usd : profile && profile.annual_owner_costs_usd;
      const annual = profile
        ? Object.keys(profile.categories_usd || {}).reduce(function (total, key) {
          return total + Number(profile.categories_usd[key] || 0);
        }, 0) + Number(housing || 0)
        : 0;
      return {
        name: destination && destination.name,
        country: destination && destination.country,
        countryGuideHref: destination && destination.countryGuideHref,
        monthlyRetirementCost: annual / 12,
      };
    }

    function decorateRecommendations(recommendations, user, projectedCapital) {
      return (recommendations || []).map(function (item) {
        const details = destinationDetails(item.destinationId, user);
        return Object.assign({}, details, item, {
          portfolioAtRetirement: Number(item.portfolioAtRetirement != null
            ? item.portfolioAtRetirement
            : projectedCapital),
          retirementTarget: item.retirementTarget == null && item.retirementTargetUsd == null
            ? null
            : Number(item.retirementTarget != null ? item.retirementTarget : item.retirementTargetUsd),
          surplusGap: item.surplusGap == null && item.surplusGapUsd == null
            ? null
            : Number(item.surplusGap != null ? item.surplusGap : item.surplusGapUsd),
          annualProjection: Array.isArray(item.annualProjection) ? item.annualProjection : [],
        });
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
        group.querySelectorAll("input, select, textarea").forEach(function (control) {
          control.disabled = group.hidden;
        });
      });
      element("finder-own-guidance").hidden = selected("finder-housing-plan") !== "own";
      element("finder-submit").disabled = selected("finder-housing-plan") === "own";
      syncTaxControls();
      updateWizardStep();
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
        returnBasis: "after_fees_and_tax",
        taxMode: selectedTaxMode(),
        taxProfile: {
          stayMode: "full_relocation",
          dependableIncome: incomeStreams().reduce(function (total, stream) {
            return total + Number(stream.amount || 0);
          }, 0),
        },
        generalInflation: 0.026,
        emergencyReserveMonths: 12,
        incomeStreams: incomeStreams(),
        preferences: {
          region: selected("finder-region"),
          settings: selectedSettings(),
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
      if (invalidMoney) errors.push("Enter a valid amount in the highlighted field.");
      if (!(user.retirementAge > user.currentAge)) errors.push("Retirement age must be later than your current age.");
      if (user.totalLiquidCapital < 0) errors.push("Capital today cannot be negative.");
      if (user.monthlyPortfolioContribution < 0) errors.push("Monthly investing cannot be negative.");
      if (user.expectedPortfolioReturn < -0.05 || user.expectedPortfolioReturn > 0.15) {
        errors.push("Expected return must be between -5% and 15%.");
      }
      if (user.housingPlan === "buy_now" && user.maximumPropertyAllocation <= 0) {
        errors.push("Enter your property purchase budget.");
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
        group.addEventListener("click", function () {
          showTooltip(group);
          const strongest = currentRecommendations[0] || {};
          track("retirement_destination_finder_projection_click", {
            chart: "capital_projection",
            point_index: Number(group.dataset.yearIndex),
            point_count: count,
            strongest_destination_id: strongest.destinationId || "none",
            strongest_tier: strongest.tier || "none",
          });
        });
      });
      figure.hidden = false;
      fallback.hidden = true;
    }

    function resultRow(item, user, matchRank) {
      const propertyBits = user.housingPlan === "buy_now" && !user.sharedSnapshot
        ? '<div><dt>Property equity</dt><dd>' + displayResultMoney(item.propertyEquity) +
          '</dd></div><div><dt>Mortgage remaining</dt><dd>' + displayResultMoney(item.mortgageBalance) + "</dd></div>"
        : "";
      const rental = user.housingPlan === "buy_now" && user.useBeforeRetirement === "rental" && !user.sharedSnapshot
        ? '<div><dt>Annual property cash flow</dt><dd>' + displayResultMoney(item.netRentalCashFlow) + "</dd></div>"
        : "";
      const financing = user.housingPlan === "buy_now" && !user.sharedSnapshot
        ? '<p class="finder-financing"><strong>' + escapeHtml(item.financingStatus) + "</strong>" +
          (item.financingReason ? " — " + escapeHtml(item.financingReason) : "") + "</p>"
        : "";
      const dossierHref = safeDossierHref(item.destinationId);
      const detailHref = safeDetailHref({
        destinationId: item.destinationId,
        household: user.household,
        housingPlan: user.housingPlan,
      });
      const countryGuide = item.countryGuideHref
        ? '<a href="' + escapeHtml(item.countryGuideHref) + '" data-finder-destination data-destination-id="' +
          escapeHtml(item.destinationId) + '" data-surface="recommended_match" data-match-rank="' + matchRank +
          '" data-tier="' + escapeHtml(item.tier) + '" data-action="country_guide">Country guide</a>'
        : "";
      const trackingAttributes = ' data-finder-destination data-destination-id="' +
        escapeHtml(item.destinationId) + '" data-surface="recommended_match" data-match-rank="' +
        matchRank + '" data-tier="' + escapeHtml(item.tier) + '"';
      const unavailableTax = item.taxStatus === "unavailable" || !Number.isFinite(Number(item.retirementTarget));
      const afterTax = taxResultPresentation(item);
      const hasRemainingCapital = !unavailableTax && Number(item.surplusGap) >= 0;
      const gapLabel = hasRemainingCapital ? "Capital remaining" : "Capital gap";
      const gapAmount = Math.abs(Number(item.surplusGap) || 0);
      const range = Array.isArray(item.retirementTargetRange) ? item.retirementTargetRange : [];
      const targetMarkup = unavailableTax
        ? "Unavailable"
        : displayResultMoney(item.retirementTarget);
      const gapMarkup = unavailableTax ? "Unavailable" : displayResultMoney(gapAmount);
      const rangeMarkup = !unavailableTax && Number.isFinite(Number(range[0])) && Number.isFinite(Number(range[1]))
        ? '<div><dt>0%–100% realized-gain range</dt><dd>' + displayResultMoney(range[0]) + "–" +
          displayResultMoney(range[1]) + "</dd></div>"
        : "";
      const taxNote = unavailableTax
        ? '<p class="finder-financing">Tax-adjusted result unavailable. ' +
          escapeHtml(item.taxReason || "Current evidence needs review.") + "</p>"
        : afterTax
          ? '<p class="finder-financing">' + escapeHtml(afterTax.note) + "</p>"
          : "";
      return '<article class="finder-result"><header><div><p class="finder-tier">' +
        escapeHtml(tierLabel(item.tier)) + '</p><h3><a href="' + escapeHtml(dossierHref) +
        '" data-finder-dossier' + trackingAttributes + ' data-action="dossier">' + escapeHtml(item.name) + "</a>" +
        '</h3><p class="finder-place">' + escapeHtml(item.country) +
        '</p></div></header><dl>' +
        '<div><dt>' + escapeHtml(afterTax ? afterTax.targetLabel : "Estimate (50% realized gains)") +
        '</dt><dd>' + targetMarkup + "</dd></div>" +
        '<div><dt>' + gapLabel + '</dt><dd>' + gapMarkup + "</dd></div>" + rangeMarkup +
        propertyBits + rental + "</dl>" + financing + taxNote +
        '<p class="finder-rationale">' + escapeHtml(finderMatchExplanation({
          item: item,
          matchRank: matchRank,
          housingPlan: user.housingPlan,
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        })) + "</p>" +
        '<div class="finder-result-actions"><a href="' + escapeHtml(dossierHref) +
        '" data-finder-dossier' + trackingAttributes + ' data-action="dossier">Destination guide</a><a href="' + escapeHtml(detailHref) +
        '" data-finder-detail' + trackingAttributes + ' data-action="detailed_plan">Build a detailed plan</a>' + countryGuide + "</div>" +
        "</article>";
    }

    function renderRecommendationList() {
      element("finder-recommendations").innerHTML = currentRecommendations.slice(0, 3).map(function (item, index) {
        return resultRow(item, currentUser, index + 1);
      }).join("");
    }

    function primaryExclusionReason(items) {
      const counts = {};
      let primary = "none";
      let maximum = 0;
      (items || []).forEach(function (item) {
        const reason = String(item.reasonCode || "unknown");
        counts[reason] = (counts[reason] || 0) + 1;
        if (counts[reason] > maximum) {
          primary = reason;
          maximum = counts[reason];
        }
      });
      return primary;
    }

    function trackDestinationClick(event) {
      const link = event.target.closest("[data-finder-destination]");
      if (!link) return;
      const fields = {
        destination_id: link.dataset.destinationId || "",
        surface: link.dataset.surface || "",
        cost_rank: Number(link.dataset.costRank) || 0,
        match_rank: Number(link.dataset.matchRank) || 0,
        tier: link.dataset.tier || "",
        action: link.dataset.action || "dossier",
      };
      track("retirement_destination_finder_destination_click", fields);
      if (fields.action === "detailed_plan") {
        track("retirement_destination_finder_detail_open", fields);
      }
      if (fields.surface === "recommended_match") {
        track("retirement_destination_finder_match_guide_click", {
          destination_id: fields.destination_id,
          link_type: fields.action,
        });
      }
    }

    function renderComparison() {
      const section = element("finder-comparison");
      if (!currentRecommendations.length) {
        section.hidden = true;
        element("finder-comparison-body").innerHTML = "";
        return;
      }
      const selected = comparisonSelection({
        recommendations: currentRecommendations,
        selectedIds: comparisonIds,
      });
      comparisonIds = selected.map(function (item) { return item.destinationId; });
      element("finder-comparison-body").innerHTML = comparisonMarkup({
        recommendations: currentRecommendations,
        selectedIds: comparisonIds,
        housingPlan: currentUser.housingPlan,
        household: currentUser.household,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
      section.hidden = false;
      if (!comparisonOpened) {
        track("retirement_destination_finder_compare_open", { housing_plan: currentUser.housingPlan });
        comparisonOpened = true;
      }
    }

    function shareFallback(url, message) {
      const output = element("finder-share-url");
      output.value = url;
      output.hidden = false;
      element("finder-share-status").textContent = message;
      if (typeof output.select === "function") output.select();
    }

    function shareCurrentResults() {
      if (!currentResult || !currentUser || !root.GHARetirementFinderScenario) return;
      try {
        const scenario = root.GHARetirementFinderScenario.buildScenario({
          currency: selectedCurrency,
          projectedCapitalUsd: finderProjectedCapital({
            sharedProjection: currentResult.sharedProjection,
            recommendations: currentRecommendations,
          }),
          user: currentUser,
          result: { recommendations: currentRecommendations },
          dataReviewed: payload.asOf,
        });
        scenario.comparisonIds = comparisonIds.slice();
        const encoded = root.GHARetirementFinderScenario.encodeScenario(scenario);
        const location = root.location || {};
        const base = (location.origin || "https://globalhomeatlas.com") +
          (location.pathname || "/retirement-destination-finder/");
        const url = base + "?scenario=" + encoded;
        track("retirement_destination_finder_share", { housing_plan: currentUser.housingPlan });
        if (root.navigator && root.navigator.clipboard && typeof root.navigator.clipboard.writeText === "function") {
          root.navigator.clipboard.writeText(url).then(function () {
            element("finder-share-status").textContent = "Results link copied.";
            element("finder-share-url").hidden = true;
          }).catch(function () {
            shareFallback(url, "Copy this results link.");
          });
        } else {
          shareFallback(url, "Copy this results link.");
        }
      } catch (error) {
        element("finder-share-status").textContent = "A results link could not be created.";
      }
    }

    function renderCapitalLandscape(result) {
      const projectedCapital = finderProjectedCapital({
        sharedProjection: result.sharedProjection,
        recommendations: currentRecommendations,
      });
      element("finder-eligible-count").textContent = String(currentRecommendations.length);
      if (!currentRecommendations.length) {
        element("finder-projected-capital").textContent = "—";
        element("finder-landscape-projected").textContent = "—";
        element("finder-landscape-axis").innerHTML = "";
        element("finder-landscape-rows").innerHTML = "";
        element("finder-landscape-toggle").hidden = true;
        return;
      }
      element("finder-projected-capital").textContent = displayResultMoney(projectedCapital);
      element("finder-landscape-projected").textContent = displayResultMoney(projectedCapital);
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
      element("finder-landscape-rows").classList.remove("is-expanded");
      element("finder-landscape-toggle").hidden = markup.rowCount <= 5;
      element("finder-landscape-toggle").textContent = "View all " + markup.rowCount + " destinations";
      element("finder-landscape-toggle").setAttribute("aria-expanded", "false");
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
      element("finder-plan-summary").hidden = sharedView;
      if (!sharedView) updateReview(user);
      element("finder-within-count").textContent = String(result.summary.withinReachCount);
      currentRecommendations = decorateRecommendations(
        result.recommendations,
        user,
        finderProjectedCapital({ sharedProjection: result.sharedProjection, recommendations: result.recommendations })
      );
      const hasRecommendations = currentRecommendations.length > 0;
      element("finder-capital-landscape").hidden = !hasRecommendations;
      element("finder-matches-section").hidden = !hasRecommendations;
      element("finder-projection-section").hidden = !hasRecommendations || sharedView;
      element("finder-empty-state").hidden = hasRecommendations;
      const activeFilters = activeDestinationFilters(user.preferences || {});
      element("finder-active-filters").textContent = activeFilters.length
        ? "Showing: " + activeFilters.join(" · ")
        : "Showing all destinations";
      element("finder-empty-state").textContent = !hasRecommendations &&
        Number(result.summary.evaluatedCount) === 0 && activeFilters.length
        ? "No destinations fit " + sentenceList(activeFilters) +
          ". Try removing a setting or choosing another region."
        : "No destinations fit these choices. Try another region or adjust your housing and financing details.";
      renderCapitalLandscape(result);
      if (!sharedView) {
        renderChart(finderProjectionView({
          housingPlan: user.housingPlan,
          sharedProjection: result.sharedProjection,
          recommendations: currentRecommendations,
        }), user);
      }
      element("finder-result-read").textContent = resultSummaryRead({
        withinReachCount: result.summary.withinReachCount,
        recommendations: currentRecommendations,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
      element("finder-result-read").hidden = !hasRecommendations;
      element("finder-strongest-match").textContent = currentRecommendations.length
        ? currentRecommendations[0].name
        : "—";
      renderRecommendationList();
      renderComparison();
      element("finder-share-section").hidden = !hasRecommendations || sharedView;
      element("finder-excluded-summary").textContent = result.excluded.length
        ? result.excluded.length + " destinations are not included in these results."
        : "All destinations that fit your choices are included.";
      renderExclusions(result.excluded);
      renderEvidence(currentRecommendations);
    }

    function render(result, user) {
      sharedView = false;
      wizardView = "results";
      document.body.classList.remove("finder-wizard-editing");
      comparisonOpened = false;
      comparisonIds = [];
      currentResult = result;
      currentUser = user;
      renderCurrentResults();
      if (wizardMedia.matches) {
        form.hidden = true;
        element("finder-adjust-plan").hidden = false;
      } else {
        element("finder-adjust-plan").hidden = true;
      }
      results.hidden = false;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
      track("retirement_destination_finder_complete", {
        housing_plan: user.housingPlan,
        purchase_method: user.housingPlan === "buy_now" ? user.purchaseMethod : "not_applicable",
        currency: selectedCurrency,
        eligible_count: result.recommendations.length,
        within_reach_count: result.summary.withinReachCount,
        excluded_count: result.excluded.length,
        strongest_destination_id: result.recommendations.length ? result.recommendations[0].destinationId : "none",
        strongest_tier: result.recommendations.length ? result.recommendations[0].tier : "none",
        region: user.preferences.region,
        setting: user.preferences.settings.join("|") || "any",
        healthcare: user.preferences.healthcare,
      });
      if (!result.recommendations.length) {
        track("retirement_destination_finder_no_results", {
          housing_plan: user.housingPlan,
          purchase_method: user.housingPlan === "buy_now" ? user.purchaseMethod : "not_applicable",
          currency: selectedCurrency,
          excluded_count: result.excluded.length,
          primary_exclusion_reason: primaryExclusionReason(result.excluded),
          region: user.preferences.region,
          setting: user.preferences.settings.join("|") || "any",
          healthcare: user.preferences.healthcare,
        });
      }
    }

    function openSharedScenario() {
      const encoded = finderScenarioValue(root.location && root.location.search);
      if (!encoded) return false;
      try {
        const scenario = root.GHARetirementFinderScenario.decodeScenario(
          encoded,
          (payload.destinations || []).map(function (item) { return item.id; })
        );
        if (validPlanningRate(scenario.currency, ratesToUsd)) {
          selectedCurrency = scenario.currency;
          element("finder-currency").value = selectedCurrency;
        }
        sharedView = true;
        wizardView = "shared";
        document.body.classList.remove("finder-wizard-editing");
        comparisonIds = scenario.comparisonIds.slice();
        currentUser = {
          household: scenario.household,
          horizonYears: scenario.horizonYears,
          housingPlan: scenario.housingPlan,
          sharedSnapshot: true,
          preferences: scenario.preferences,
        };
        currentResult = {
          summary: {
            evaluatedCount: scenario.results.length,
            withinReachCount: scenario.results.filter(function (item) { return item.tier === "within_reach"; }).length,
            closeCount: scenario.results.filter(function (item) { return item.tier === "close"; }).length,
            stretchCount: scenario.results.filter(function (item) { return item.tier === "stretch"; }).length,
          },
          sharedProjection: {
            portfolioAtRetirement: scenario.projectedCapitalUsd,
            annualProjection: [],
            exhaustedMonth: null,
          },
          recommendations: scenario.results,
          excluded: [],
        };
        renderCurrentResults();
        element("finder-data-reviewed").textContent = "Data reviewed " + scenario.dataReviewed;
        element("finder-data-reviewed").hidden = false;
        if (scenario.results.length < 3) {
          element("finder-comparison-status").textContent =
            "Some destinations in this shared result are no longer available. Showing " +
            scenario.results.length + " remaining.";
        }
        results.hidden = false;
        if (wizardMedia.matches) {
          form.hidden = true;
          element("finder-adjust-plan").hidden = true;
        }
        track("retirement_destination_finder_shared_open", { housing_plan: scenario.housingPlan });
        return true;
      } catch (error) {
        element("finder-shared-error").hidden = false;
        return false;
      }
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (wizardMedia.matches && wizardStepIndex < activeWizardSectionIds().length - 1) {
        advanceWizard();
        return;
      }
      const user = collectUser();
      const errors = validate(user);
      if (errors.length) {
        showFormErrors(errors);
        return;
      }
      errorSummary.hidden = true;
      try {
        const result = root.GHARetirementDestinationFinder.recommendDestinations({
          user: user,
          destinations: payload.destinations,
          retirementCosts: payload.retirementCosts,
          mortgageProfiles: payload.mortgageProfiles,
          taxPlanning: payload.taxPlanning,
        });
        render(result, user);
      } catch (error) {
        errorSummary.textContent = error.message || "We could not complete this calculation. Review your details and try again.";
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
    element("finder-currency").value = selectedCurrency;
    element("finder-currency").addEventListener("change", function () {
      if (changePlanningCurrency(element("finder-currency").value)) {
        track("retirement_destination_finder_currency_change", { currency: selectedCurrency });
      }
    });
    [
      ["finder-region", "region"],
      ["finder-healthcare", "healthcare"],
    ].forEach(function (entry) {
      element(entry[0]).addEventListener("change", function () {
        track("retirement_destination_finder_preference_change", {
          preference: entry[1],
          value: selected(entry[0]),
        });
      });
    });
    document.querySelectorAll('[name="finder-setting"]').forEach(function (control) {
      control.addEventListener("change", function () {
        track("retirement_destination_finder_preference_change", {
          preference: "setting",
          value: control.value,
          selected: control.checked,
        });
      });
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
    element("finder-landscape-rows").addEventListener("click", trackDestinationClick);
    element("finder-landscape-toggle").addEventListener("click", function () {
      const rows = element("finder-landscape-rows");
      const toggle = element("finder-landscape-toggle");
      const expanded = !rows.classList.contains("is-expanded");
      rows.classList.toggle("is-expanded", expanded);
      toggle.setAttribute("aria-expanded", String(expanded));
      toggle.textContent = expanded
        ? "Show fewer destinations"
        : "View all " + currentRecommendations.length + " destinations";
    });
    element("finder-recommendations").addEventListener("click", trackDestinationClick);
    element("finder-comparison-body").addEventListener("change", function (event) {
      const control = event.target && event.target.dataset && event.target.dataset.comparisonPosition !== undefined
        ? event.target
        : null;
      if (!control) return;
      const position = Number(control.dataset.comparisonPosition);
      const nextIds = replaceComparisonDestination({
        recommendations: currentRecommendations,
        selectedIds: comparisonIds,
        position: position,
        destinationId: control.value,
      });
      if (nextIds.join("|") === comparisonIds.join("|")) return;
      comparisonIds = nextIds;
      renderComparison();
      element("finder-comparison-status").textContent = "Comparison updated.";
      track("retirement_destination_finder_compare_replace", {
        destination_id: control.value,
        comparison_position: position + 1,
      });
    });
    element("finder-share").addEventListener("click", shareCurrentResults);
    element("finder-wizard-next").addEventListener("click", advanceWizard);
    element("finder-wizard-back").addEventListener("click", function () {
      if (wizardStepIndex === 0) return;
      wizardStepIndex -= 1;
      showFormErrors([]);
      updateWizardStep({ focus: true });
    });
    element("finder-adjust-plan").addEventListener("click", returnToWizard);
    if (typeof wizardMedia.addEventListener === "function") {
      wizardMedia.addEventListener("change", syncWizardMode);
    }
    syncHousing();
    syncWizardMode();
    track("retirement_destination_finder_open");
    openSharedScenario();
  }

  return {
    convertPlanningAmount: convertPlanningAmount,
    convertPlanningControlAmount: convertPlanningControlAmount,
    parseMoneyInput: parseMoneyInput,
    formatMoneyInputValue: formatMoneyInputValue,
    formatPlanningMoney: formatPlanningMoney,
    resultMoney: resultMoney,
    compactResultMoney: compactResultMoney,
    housingVisibility: housingVisibility,
    taxControlVisibility: taxControlVisibility,
    taxResultPresentation: taxResultPresentation,
    activeMoneyControlIds: activeMoneyControlIds,
    safeDetailHref: safeDetailHref,
    calculatorHrefsForResults: calculatorHrefsForResults,
    safeDossierHref: safeDossierHref,
    resultSummaryRead: resultSummaryRead,
    tierLabel: tierLabel,
    finderMatchExplanation: finderMatchExplanation,
    comparisonSelection: comparisonSelection,
    replaceComparisonDestination: replaceComparisonDestination,
    comparisonMarkup: comparisonMarkup,
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
