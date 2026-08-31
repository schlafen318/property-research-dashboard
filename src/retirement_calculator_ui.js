(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementCalculatorUI = api;
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

  function convertPlanningControlAmount(input) {
    const converted = convertPlanningAmount(input);
    if (converted === null) return null;
    const step = Number(input.step);
    if (!(step > 0)) return Math.round(converted);
    return Math.round(converted / step) * step;
  }

  function planningControlConversionStep(input) {
    if (input.controlId === "ret-monthly-spending" && input.monthlySpendingIsAutomatic) {
      return 100;
    }
    return Number(input.controlStep);
  }

  function preferredPlanningCurrency() {
    return "USD";
  }

  function retirementCalculatorViewState(input) {
    const mobile = Boolean(input && input.mobile);
    const hasResult = Boolean(input && input.hasResult);
    const hasEditSnapshot = Boolean(input && input.hasEditSnapshot);
    const requestedMode = input && input.requestedMode === "results" ? "results" : "editing";
    if (!mobile) {
      return {
        mode: "split",
        formHidden: false,
        resultsHidden: false,
        backHidden: true,
      };
    }
    if (hasResult && requestedMode === "results") {
      return {
        mode: "results",
        formHidden: true,
        resultsHidden: false,
        backHidden: true,
      };
    }
    return {
      mode: "editing",
      formHidden: false,
      resultsHidden: true,
      backHidden: !hasEditSnapshot,
    };
  }

  function retirementCalculatorViewportAction(input) {
    const leavingMobile = Boolean(input && input.wasMobile) && !Boolean(input && input.isMobile);
    const hasPendingMobileEdit = input && input.requestedMode === "editing" && Boolean(input.hasEditSnapshot);
    const recalculate = Boolean(leavingMobile && hasPendingMobileEdit);
    return {
      recalculate: recalculate,
      clearEditSnapshot: recalculate,
    };
  }

  function retirementCalculatorViewportResolution(input) {
    return {
      clearEditSnapshot: true,
      restoreSnapshot: !Boolean(input && input.recalculated),
    };
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
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
    }).format(amount);
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

  function annualSpendingFromMonthly(monthlySpending) {
    return Number(monthlySpending) * 12;
  }

  function roundToNearestHundred(amount) {
    return Math.round(Number(amount) / 100) * 100;
  }

  function illustrativeReturnExample() {
    return 4;
  }

  function currentCostComparison(input) {
    const currentMonthly = Number(input.currentMonthly);
    const destinationMonthly = Number(input.destinationMonthly);
    if (!(currentMonthly > 0) || !(destinationMonthly > 0)) return null;
    const difference = destinationMonthly - currentMonthly;
    const maximum = Math.max(currentMonthly, destinationMonthly);
    return {
      direction: difference < 0 ? "lower" : difference > 0 ? "higher" : "same",
      monthlyDifference: Math.abs(difference),
      annualDifference: Math.abs(difference) * 12,
      percentDifference: Math.round(Math.abs(difference) / currentMonthly * 100),
      currentBarPercent: currentMonthly / maximum * 100,
      destinationBarPercent: destinationMonthly / maximum * 100,
    };
  }

  function retirementTargetComparison(input) {
    const currentTarget = Number(input.currentTarget);
    const destinationTarget = Number(input.destinationTarget);
    if (!Number.isFinite(currentTarget) || !Number.isFinite(destinationTarget) ||
        currentTarget < 0 || destinationTarget < 0) return null;
    const difference = destinationTarget - currentTarget;
    return {
      direction: difference < 0 ? "lower" : difference > 0 ? "higher" : "same",
      targetDifference: Math.abs(difference),
      percentDifference: currentTarget === 0
        ? null
        : Math.round(Math.abs(difference) / currentTarget * 100),
    };
  }

  function housingAmount(profile, plan) {
    return plan === "rent" ? profile.annual_rent_usd : profile.annual_owner_costs_usd;
  }

  function annualBenchmark(input) {
    const categories = Object.values(input.profile.categories_usd).reduce(function (total, value) {
      return total + Number(value);
    }, 0);
    return categories + Number(housingAmount(input.profile, input.plan));
  }

  function rankDestinationCosts(input) {
    return input.destinations.map(function (record) {
      const profile = record.profiles[input.household];
      return {
        destinationId: record.destination_id,
        name: record.name,
        monthlyCost: Math.round(annualBenchmark({ profile: profile, plan: input.plan }) / 12),
      };
    }).sort(function (left, right) {
      return left.monthlyCost - right.monthlyCost || left.name.localeCompare(right.name);
    });
  }

  function usesPropertyBudget(plan) {
    return plan === "buy_now" || plan === "buy_retirement";
  }

  function housingGuidance(plan) {
    if (plan === "rent") return "Monthly retirement living expenses, including rent.";
    if (plan === "own") return "Monthly retirement living expenses, including owner running costs; no new home purchase.";
    if (plan === "buy_now") {
      return "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase.";
    }
    return "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase at retirement.";
  }

  function housingExpenseLabels(plan) {
    if (plan === "rent") {
      return {
        input: "Monthly retirement living expenses including rent",
        result: "Annual spending incl. rent",
      };
    }
    return {
      input: "Monthly retirement living expenses including owner costs",
      result: "Annual spending incl. owner costs",
    };
  }

  function accumulationChartModel(input) {
    const series = input.series;
    const targetValue = Number(input.targetValue);
    const maximum = Math.max.apply(null, series.map(function (point) {
      return Number(point.totalValue);
    }).concat([targetValue, 1]));
    return {
      maximum: maximum,
      targetY: 258 - targetValue / maximum * 240,
      years: series.map(function (point) {
        return {
          year: Number(point.year),
          lumpSumValue: Number(point.lumpSumValue),
          contributionValue: Number(point.contributionValue),
          totalValue: Number(point.totalValue),
          lumpHeight: Number(point.lumpSumValue) / maximum * 240,
          contributionHeight: Number(point.contributionValue) / maximum * 240,
        };
      }),
    };
  }

  function sensitivityRates(selectedRate) {
    const selected = Number(selectedRate);
    function normalized(value) { return Math.round(value * 10000) / 10000; }
    return [
      { key: "lower", label: "Lower return", rate: normalized(selected - 0.01) },
      { key: "selected", label: "Your assumption", rate: normalized(selected) },
      { key: "higher", label: "Higher return", rate: normalized(selected + 0.01) },
    ];
  }

  function planningSummary(input) {
    const result = input && input.result ? input.result : input;
    const currency = input && input.currency ? input.currency : "USD";
    const ratesToUsd = input && input.ratesToUsd ? input.ratesToUsd : { USD: 1 };
    const format = function (amountUsd) {
      return formatPlanningMoney({ amountUsd: amountUsd, currency: currency, ratesToUsd: ratesToUsd });
    };
    const investment = format(Number(result.investmentNeededToday));
    const contribution = format(Number(result.monthlyContributionToday));
    const home = Number(result.homePurchaseNeededToday);
    if (home > 0) {
      return "Invest " + investment + " today and " + contribution +
        " per month for retirement, plus " + format(home) + " for the home purchase.";
    }
    return "Invest " + investment + " today and " + contribution +
      " per month to fund this retirement plan.";
  }

  function accumulationTooltipContent(input) {
    const point = input.point;
    const projectedAge = Number(input.currentAge) + Number(point.year);
    const format = function (amountUsd) {
      return formatPlanningMoney({
        amountUsd: amountUsd,
        currency: input.currency || "USD",
        ratesToUsd: input.ratesToUsd || { USD: 1 },
      });
    };
    const lumpSum = format(Number(point.lumpSumValue));
    const contributions = format(Number(point.contributionValue));
    const total = format(Number(point.totalValue));
    return {
      heading: "Year " + point.year + " · age " + projectedAge,
      lumpSum: lumpSum,
      contributions: contributions,
      total: total,
      accessibleLabel: "Year " + point.year + ", age " + projectedAge +
        ". Lump sum and growth " + lumpSum +
        ". Contributions and growth " + contributions +
        ". Total " + total + ".",
    };
  }

  function isInvalidNumericControl(control) {
    if (control.disabled) return false;
    const valid = typeof control.checkValidity === "function" ? control.checkValidity() : control.valid !== false;
    return control.value === "" || !valid;
  }

  function isNegativeRate(value) {
    return Number(value) < 0;
  }

  function isBenchmarkPanelHidden(input) {
    return input.panel !== input.selected;
  }

  function partitionBenchmarkRows(input) {
    const matching = input.rows.filter(function (row) {
      return input.selectedContinent === "all" || row.continent === input.selectedContinent;
    });
    const excluded = input.rows.filter(function (row) {
      return input.selectedContinent !== "all" && row.continent !== input.selectedContinent;
    });
    const visibleCount = input.visibleCount || 10;
    return {
      visible: matching.slice(0, visibleCount),
      expandable: matching.slice(visibleCount),
      excluded: excluded,
    };
  }

  function initRetirementBenchmarkTable(selectId, continentSelectId) {
    if (!root) return;
    const select = document.getElementById(selectId);
    const continentSelect = document.getElementById(continentSelectId);
    const panels = Array.from(document.querySelectorAll("[data-benchmark-panel]"));
    if (!select || panels.length === 0) return;
    const panelRows = new Map();
    panels.forEach(function (panel) {
      panelRows.set(panel, Array.from(panel.querySelectorAll(".benchmark-row")));
    });

    function syncPanels() {
      panels.forEach(function (panel) {
        panel.hidden = isBenchmarkPanelHidden({
          panel: panel.dataset.benchmarkPanel,
          selected: select.value,
        });
        const partition = partitionBenchmarkRows({
          rows: panelRows.get(panel).map(function (row) {
            return { row: row, continent: row.dataset.continent };
          }),
          selectedContinent: continentSelect ? continentSelect.value : "all",
          visibleCount: 10,
        });
        const visibleBody = panel.querySelector("[data-benchmark-visible]");
        const expandableBody = panel.querySelector("[data-benchmark-expandable]");
        const more = panel.querySelector("[data-benchmark-more]");
        const summary = panel.querySelector("[data-benchmark-summary]");
        partition.excluded.forEach(function (item) { item.row.hidden = true; });
        partition.visible.forEach(function (item) {
          item.row.hidden = false;
          visibleBody.appendChild(item.row);
        });
        partition.expandable.forEach(function (item) {
          item.row.hidden = false;
          expandableBody.appendChild(item.row);
        });
        more.hidden = partition.expandable.length === 0;
        more.open = false;
        summary.textContent = continentSelect && continentSelect.value !== "all"
          ? "View remaining " + partition.expandable.length + " destinations"
          : "View ranks 11–30";
      });
    }

    select.addEventListener("change", syncPanels);
    if (continentSelect) continentSelect.addEventListener("change", syncPanels);
    syncPanels();
  }

  function initRetirementCalculator(rootId, payload) {
    if (!root) return;
    const form = document.getElementById(rootId);
    const engine = root.GHARetirementCalculator;
    if (!form || !engine || !payload || !Array.isArray(payload.destinations)) return;

    const byId = Object.fromEntries(payload.destinations.map(function (item) {
      return [item.destination_id, item];
    }));
    const el = function (id) { return document.getElementById(id); };
    const number = function (id) { return Number(el(id).value); };
    const rate = function (id) { return number(id) / 100; };
    const currencyConfig = payload.planning_currencies || { as_of: "", rates_to_usd: { USD: 1 } };
    const ratesToUsd = currencyConfig.rates_to_usd || { USD: 1 };
    const initialCurrency = preferredPlanningCurrency();
    let selectedCurrency = "USD";
    const displayMoney = function (amountUsd) {
      return formatPlanningMoney({ amountUsd: amountUsd, currency: selectedCurrency, ratesToUsd: ratesToUsd });
    };
    const toUsd = function (amount, currency) {
      return convertPlanningAmount({
        amount: amount,
        fromCurrency: currency || selectedCurrency,
        toCurrency: "USD",
        ratesToUsd: ratesToUsd,
      });
    };
    const fromUsd = function (amountUsd, currency) {
      return convertPlanningAmount({
        amount: amountUsd,
        fromCurrency: "USD",
        toCurrency: currency || selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
    };
    const moneyNumber = function (id) {
      const amount = parseMoneyInput(el(id).value);
      return Number(toUsd(amount === null ? 0 : amount) || 0);
    };
    const moneyControlIds = [
      "ret-monthly-spending",
      "ret-property-budget",
      "ret-monthly-income",
      "ret-pension",
      "ret-other-income",
      "ret-rental-income",
      "ret-current-monthly-spending",
    ];
    const formatMoneyControl = function (control) {
      if (!control || control.value === "") return;
      const amount = parseMoneyInput(control.value);
      if (amount !== null) control.value = formatMoneyInputValue(amount);
    };
    const validateMoneyControl = function (control) {
      if (control.disabled) {
        control.setCustomValidity("");
        control.removeAttribute("aria-invalid");
        return false;
      }
      const invalid = isInvalidMoneyInput({
        value: control.value,
        min: control.min,
        step: control.step,
      });
      control.setCustomValidity(invalid ? "Enter a valid amount." : "");
      if (invalid) control.setAttribute("aria-invalid", "true");
      else control.removeAttribute("aria-invalid");
      return invalid;
    };
    let benchmarkValue = 0;
    let monthlySpendingIsAutomatic = true;
    let autoCalculationTimer = null;
    let hasTrackedResult = false;
    let hasTrackedCurrentCostComparison = false;
    let latestResult = null;
    let requestedViewMode = "editing";
    let editSnapshot = null;
    const mobileQuery = typeof root.matchMedia === "function"
      ? root.matchMedia("(max-width: 780px)")
      : { matches: false };
    let wasMobile = mobileQuery.matches;

    const prefill = retirementPrefill(root.location && root.location.search);
    [
      ["ret-destination", prefill.destination],
      ["ret-household", prefill.household],
      ["ret-housing-plan", prefill.housing],
    ].forEach(function (entry) {
      if (!entry[1]) return;
      const control = el(entry[0]);
      const match = Array.from(control.options).some(function (option) {
        return option.value === entry[1];
      });
      if (match) control.value = entry[1];
    });
    el("ret-currency").value = selectedCurrency;

    function selectedRecord() {
      return byId[el("ret-destination").value];
    }

    function syncDestinationDefaults(resetPropertyBudget, preserveValues) {
      const record = selectedRecord();
      if (!record) return;
      const profile = record.profiles[el("ret-household").value];
      const plan = el("ret-housing-plan").value;
      const expenseLabels = housingExpenseLabels(plan);
      benchmarkValue = annualBenchmark({ profile: profile, plan: plan });
      if (!preserveValues) {
        monthlySpendingIsAutomatic = true;
        el("ret-monthly-spending").value = formatMoneyInputValue(roundToNearestHundred(fromUsd(benchmarkValue / 12)));
      }
      el("ret-monthly-spending-label").textContent = expenseLabels.input;
      el("ret-first-expenses-label").textContent = expenseLabels.result;
      el("ret-housing-guidance").textContent = housingGuidance(plan);
      el("ret-property-field").hidden = !usesPropertyBudget(plan);
      el("ret-property-budget").disabled = !usesPropertyBudget(plan);
      const acquisitionCostRate = Number(record.property.acquisition_cost_rate || 0);
      const acquisitionCostBasis = String(record.property.acquisition_cost_basis || "").trim();
      el("ret-acquisition-cost-guidance").textContent = acquisitionCostBasis || (
        acquisitionCostRate > 0
          ? "The model adds a " + (acquisitionCostRate * 100).toFixed(1).replace(/\.0$/, "") + "% acquisition-cost allowance. Obtain a buyer-specific closing statement."
          : "No acquisition-cost allowance is included. Add a buyer-specific closing-cost estimate before relying on the total."
      );
      if (resetPropertyBudget) {
        el("ret-property-budget").value = formatMoneyInputValue(
          Math.round(fromUsd(Number(record.property.representative_price_usd)))
        );
      }
      if (!preserveValues) {
        el("ret-general-inflation").value = String(record.inflation.general * 100);
        el("ret-healthcare-inflation").value = String(record.inflation.healthcare * 100);
        el("ret-property-inflation").value = String(record.inflation.property * 100);
      }
    }

    function captureFormState() {
      return {
        monthlySpendingIsAutomatic: monthlySpendingIsAutomatic,
        controls: Array.from(form.elements).filter(function (control) {
          return control.id && !["button", "submit"].includes(control.type);
        }).map(function (control) {
          return {
            id: control.id,
            value: control.value,
            checked: Boolean(control.checked),
          };
        }),
      };
    }

    function restoreFormState(snapshot) {
      if (!snapshot) return;
      snapshot.controls.forEach(function (saved) {
        const control = el(saved.id);
        if (!control) return;
        control.value = saved.value;
        if (control.type === "checkbox" || control.type === "radio") control.checked = saved.checked;
      });
      monthlySpendingIsAutomatic = snapshot.monthlySpendingIsAutomatic;
      selectedCurrency = el("ret-currency").value;
      syncDestinationDefaults(false, true);
      updateMonthlyInvestmentPreview();
    }

    function focusSection(section) {
      if (!section) return;
      section.scrollIntoView({ behavior: "smooth", block: "start" });
      section.focus({ preventScroll: true });
    }

    function applyCalculatorView() {
      const state = retirementCalculatorViewState({
        mobile: mobileQuery.matches,
        hasResult: Boolean(latestResult),
        requestedMode: requestedViewMode,
        hasEditSnapshot: Boolean(editSnapshot),
      });
      form.hidden = state.formHidden;
      el("ret-results").hidden = state.resultsHidden;
      el("ret-back-results").hidden = state.backHidden;
      el("ret-adjust-plan").hidden = !latestResult;
      document.body.classList.toggle("ret-mobile-results", state.mode === "results");
      document.body.classList.toggle("ret-mobile-editing", state.mode === "editing" && mobileQuery.matches);
      return state;
    }

    function showResults() {
      requestedViewMode = "results";
      editSnapshot = null;
      const state = applyCalculatorView();
      if (state.mode === "results") focusSection(el("ret-results"));
    }

    function editPlan() {
      if (mobileQuery.matches) {
        editSnapshot = captureFormState();
        requestedViewMode = "editing";
        applyCalculatorView();
      }
      focusSection(form);
      track("retirement_calculator_adjust_plan");
    }

    function returnToResults() {
      root.clearTimeout(autoCalculationTimer);
      restoreFormState(editSnapshot);
      if (latestResult) render(latestResult);
      showResults();
    }

    function handleViewportChange() {
      const isMobile = mobileQuery.matches;
      const action = retirementCalculatorViewportAction({
        wasMobile: wasMobile,
        isMobile: isMobile,
        requestedMode: requestedViewMode,
        hasEditSnapshot: Boolean(editSnapshot),
      });
      wasMobile = isMobile;
      if (action.recalculate) {
        const recalculated = calculate(null);
        const resolution = retirementCalculatorViewportResolution({ recalculated: recalculated });
        if (resolution.restoreSnapshot) {
          restoreFormState(editSnapshot);
          if (latestResult) render(latestResult);
          el("ret-errors").textContent = "";
        }
        if (resolution.clearEditSnapshot) editSnapshot = null;
      }
      applyCalculatorView();
    }

    function renderDestinationCosts() {
      const chart = el("ret-cost-sidecar-chart");
      const context = el("ret-cost-sidecar-context");
      const household = el("ret-household").value;
      const plan = el("ret-housing-plan").value;
      const rows = rankDestinationCosts({
        destinations: payload.destinations,
        household: household,
        plan: plan,
      });
      const maximum = rows.length ? rows[rows.length - 1].monthlyCost : 1;
      const currentId = el("ret-destination").value;
      context.textContent = el("ret-household").selectedOptions[0].textContent + " · Monthly " + selectedCurrency + " " +
        (plan === "rent" ? "including rent" : "including owner running costs");
      chart.replaceChildren();
      rows.forEach(function (row, index) {
        const button = document.createElement("button");
        const heading = document.createElement("span");
        const name = document.createElement("strong");
        const amount = document.createElement("span");
        const track = document.createElement("span");
        const fill = document.createElement("span");
        button.type = "button";
        button.className = "cost-row";
        button.dataset.destinationId = row.destinationId;
        button.setAttribute("aria-label", "Select " + row.name + ", " + displayMoney(row.monthlyCost) +
          " per month, rank " + (index + 1) + " of " + rows.length);
        if (row.destinationId === currentId) {
          button.classList.add("is-current");
          button.setAttribute("aria-current", "true");
        }
        heading.className = "cost-row-heading";
        name.textContent = (index + 1) + ". " + row.name;
        amount.textContent = displayMoney(row.monthlyCost) + "/mo";
        track.className = "cost-bar-track";
        track.setAttribute("aria-hidden", "true");
        fill.className = "cost-bar-fill";
        fill.style.width = Math.max(2, row.monthlyCost / maximum * 100).toFixed(1) + "%";
        heading.append(name, amount);
        track.appendChild(fill);
        button.append(heading, track);
        button.addEventListener("click", function () {
          el("ret-destination").value = row.destinationId;
          el("ret-destination").dispatchEvent(new Event("change", { bubbles: true }));
          el("ret-cost-sidecar").close();
        });
        chart.appendChild(button);
      });
      return chart.querySelector(".is-current") || chart.querySelector(".cost-row");
    }

    function initDestinationCostSidecar() {
      const sidecar = el("ret-cost-sidecar");
      const opener = el("ret-cost-compare-open");
      const closer = el("ret-cost-sidecar-close");
      if (!sidecar || !opener || !closer || typeof sidecar.showModal !== "function") return;
      opener.addEventListener("click", function () {
        const focusTarget = renderDestinationCosts();
        sidecar.showModal();
        if (focusTarget) focusTarget.focus();
        track("retirement_calculator_cost_compare_open");
      });
      closer.addEventListener("click", function () { sidecar.close(); });
      sidecar.addEventListener("click", function (event) {
        if (event.target === sidecar) sidecar.close();
      });
      sidecar.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && sidecar.open) {
          event.preventDefault();
          sidecar.close();
        }
      });
      sidecar.addEventListener("close", function () { opener.focus(); });
    }

    function expenseCategories(record, profile, plan, monthlySpendingOverride) {
      const generalRate = rate("ret-general-inflation");
      const healthcareRate = rate("ret-healthcare-inflation");
      const propertyRate = rate("ret-property-inflation");
      const monthlySpending = monthlySpendingOverride === undefined
        ? moneyNumber("ret-monthly-spending")
        : Number(monthlySpendingOverride);
      const annualSpending = annualSpendingFromMonthly(monthlySpending);
      const scale = benchmarkValue > 0 ? annualSpending / benchmarkValue : 1;
      const categories = Object.entries(profile.categories_usd).map(function (entry) {
        return {
          amount: Number(entry[1]) * scale,
          inflationRate: entry[0] === "private_healthcare" ? healthcareRate : generalRate,
        };
      });
      categories.push({
        amount: Number(housingAmount(profile, plan)) * scale,
        inflationRate: plan === "rent" ? generalRate : propertyRate,
      });
      return categories;
    }

    function calculatorInput(planOverride, monthlySpendingOverride) {
      const record = selectedRecord();
      if (!record) throw new Error("Choose a destination with available cost data");
      const household = el("ret-household").value;
      const profile = record.profiles[household];
      const plan = planOverride || el("ret-housing-plan").value;
      const generalRate = rate("ret-general-inflation");
      return {
        currentAge: number("ret-current-age"),
        retirementAge: number("ret-retirement-age"),
        horizonYears: number("ret-horizon"),
        expenseCategories: expenseCategories(record, profile, plan, monthlySpendingOverride),
        incomeStreams: [
          { amount: moneyNumber("ret-pension"), indexed: el("ret-pension-indexed").checked, inflationRate: generalRate },
          { amount: moneyNumber("ret-other-income"), indexed: el("ret-other-indexed").checked, inflationRate: generalRate },
          { amount: moneyNumber("ret-rental-income"), indexed: el("ret-rental-indexed").checked, inflationRate: generalRate },
        ],
        housingPlan: plan,
        propertyPrice: moneyNumber("ret-property-budget"),
        propertyInflation: rate("ret-property-inflation"),
        acquisitionCostRate: Number(record.property.acquisition_cost_rate),
        generalInflation: generalRate,
        emergencyReserveMonths: number("ret-reserve-months"),
        expectedPortfolioReturn: rate("ret-expected-return"),
        monthlyIncomeBeforeRetirement: moneyNumber("ret-monthly-income"),
        incomeInvestedRate: rate("ret-income-invested-rate"),
      };
    }

    function setMoney(id, value) {
      el(id).textContent = displayMoney(value);
    }

    function horizonBand(years) {
      if (years <= 25) return "up_to_25";
      if (years <= 30) return "26_to_30";
      if (years <= 35) return "31_to_35";
      return "over_35";
    }

    function trackingContext() {
      return {
        destination_id: el("ret-destination").value,
        household_type: el("ret-household").value,
        housing_plan: el("ret-housing-plan").value,
        horizon_band: horizonBand(number("ret-horizon")),
      };
    }

    function track(name) {
      if (root.GHA && typeof root.GHA.track === "function") root.GHA.track(name, trackingContext());
    }

    function renderCurrentCostComparison(resultOverride) {
      const section = el("ret-current-cost-comparison");
      const result = el("ret-current-cost-result");
      const destination = selectedRecord();
      const retirementResult = resultOverride || latestResult;
      const currentMonthly = moneyNumber("ret-current-monthly-spending");
      const comparison = currentCostComparison({
        currentMonthly: currentMonthly,
        destinationMonthly: moneyNumber("ret-monthly-spending"),
      });
      section.hidden = false;
      if (!comparison || !destination || !retirementResult) {
        result.hidden = true;
        return;
      }
      const enteredLocation = el("ret-current-location").value.trim();
      const currentLabel = enteredLocation || "Where you live now";
      const destinationLabel = destination.name;
      el("ret-current-cost-label").textContent = currentLabel;
      el("ret-current-cost-destination-label").textContent = destinationLabel;
      el("ret-current-target-label").textContent = currentLabel;
      el("ret-destination-target-label").textContent = destinationLabel;
      setMoney("ret-current-cost-amount", moneyNumber("ret-current-monthly-spending"));
      setMoney("ret-current-cost-destination-amount", moneyNumber("ret-monthly-spending"));
      el("ret-current-cost-bar").style.width = comparison.currentBarPercent.toFixed(1) + "%";
      el("ret-current-cost-destination-bar").style.width = comparison.destinationBarPercent.toFixed(1) + "%";
      const currentRetirementResult = engine.calculateRetirement(calculatorInput(undefined, currentMonthly));
      const targets = retirementTargetComparison({
        currentTarget: currentRetirementResult.liquidPortfolio + currentRetirementResult.emergencyReserve,
        destinationTarget: retirementResult.liquidPortfolio + retirementResult.emergencyReserve,
      });
      setMoney("ret-current-target", currentRetirementResult.liquidPortfolio + currentRetirementResult.emergencyReserve);
      setMoney("ret-destination-target", retirementResult.liquidPortfolio + retirementResult.emergencyReserve);
      if (comparison.direction === "same") {
        el("ret-current-cost-summary").textContent = destinationLabel +
          " is about the same per month as " + currentLabel + ".";
        el("ret-current-cost-annual").textContent = "No modeled annual difference at these spending levels.";
      } else {
        el("ret-current-cost-summary").textContent = destinationLabel + " is " +
          displayMoney(comparison.monthlyDifference) + " " +
          (comparison.direction === "lower" ? "less" : "more") + " per month (" +
          comparison.percentDifference + "% " + comparison.direction + ") than " + currentLabel + ".";
        el("ret-current-cost-annual").textContent = "That is about " +
          displayMoney(comparison.annualDifference) + " " +
          (comparison.direction === "lower" ? "less" : "more") + " per year.";
      }
      if (targets.direction === "same") {
        el("ret-target-difference").textContent = "The modeled retirement funding targets are about the same.";
      } else {
        el("ret-target-difference").textContent = "The destination target is " +
          displayMoney(targets.targetDifference) + " " +
          (targets.direction === "lower" ? "lower" : "higher") +
          (targets.percentDifference === null ? "." : " (" + targets.percentDifference + "%).");
      }
      result.hidden = false;
      if (!hasTrackedCurrentCostComparison) {
        track("retirement_calculator_current_cost_compare");
        hasTrackedCurrentCostComparison = true;
      }
    }

    function render(result) {
      const record = selectedRecord();
      latestResult = result;
      el("ret-detailed-projection").hidden = false;
      el("ret-plan-summary").textContent = planningSummary({
        result: result,
        currency: selectedCurrency,
        ratesToUsd: ratesToUsd,
      });
      setMoney("ret-total-today", result.totalNeededToday);
      setMoney("ret-invest-today", result.investmentNeededToday);
      setMoney("ret-home-today", result.homePurchaseNeededToday);
      setMoney("ret-monthly-contribution", result.monthlyContributionToday);
      setMoney("ret-contribution-retirement", result.contributionValueAtRetirement);
      setMoney("ret-total-retirement", result.totalCapitalAtRetirement);
      setMoney("ret-total-retirement-summary", result.totalCapitalAtRetirement);
      setMoney("ret-liquid-portfolio", result.liquidPortfolio);
      setMoney("ret-property-retirement", result.propertyTiming === "retirement" ? result.propertyCapital : 0);
      setMoney("ret-emergency-reserve", result.emergencyReserve);
      setMoney("ret-first-expenses", result.firstYearExpenses);
      setMoney("ret-outside-income", result.outsideIncome);
      setMoney("ret-funding-gap", result.fundingGap);
      el("ret-result-return").textContent = (result.expectedPortfolioReturn * 100).toFixed(2).replace(/\.00$/, "") + "%";
      el("ret-result-implied-withdrawal").textContent = result.impliedFirstYearWithdrawal === null
        ? "—"
        : (result.impliedFirstYearWithdrawal * 100).toFixed(2) + "%";
      const netReturn = el("ret-result-net-return");
      const netReturnIsNegative = result.netReturnAfterWithdrawal !== null && isNegativeRate(result.netReturnAfterWithdrawal);
      netReturn.textContent = result.netReturnAfterWithdrawal === null
        ? "—"
        : (result.netReturnAfterWithdrawal * 100).toFixed(2) + "%";
      netReturn.classList.toggle("is-negative", netReturnIsNegative);
      el("ret-net-return-explanation").textContent = netReturnIsNegative
        ? "Expected return minus first-year portfolio withdrawal. Withdrawals exceed the assumed return."
        : "Expected return minus first-year portfolio withdrawal.";
      el("ret-home-today-label").textContent = result.propertyTiming === "today"
        ? "Home purchase needed now"
        : "Home purchase today";
      el("ret-home-summary").hidden = result.propertyTiming !== "today";
      el("ret-property-retirement-label").textContent = result.propertyTiming === "retirement"
        ? "Home purchase at retirement"
        : "No home purchase at retirement";
      el("ret-result-status").textContent = record.name + " · " + el("ret-household").selectedOptions[0].textContent + " · " + result.yearsToRetirement + " years to retirement";
      renderSensitivity();
      renderHousingComparison();
      renderAccumulationChart(result.annualAccumulation, result.totalCapitalAtRetirement);
      renderCurrentCostComparison();
      el("ret-result-assumptions").textContent =
        "Data " + payload.as_of + " · " + record.confidence.overall + " confidence · " +
        "uses the same expected return every year. Actual return order and market losses can materially change the outcome. " +
        "Planning estimate only; not financial, tax, legal, immigration, healthcare, or investment advice.";
      el("ret-save-action").hidden = false;
      applyCalculatorView();
      if (!hasTrackedResult) {
        track("retirement_calculator_result_view");
        hasTrackedResult = true;
      }
    }

    function appendComparisonRow(container, label, rateLabel, value, isSelected) {
      const row = document.createElement("tr");
      const name = document.createElement("th");
      const rateCell = document.createElement("td");
      const valueCell = document.createElement("td");
      name.scope = "row";
      name.textContent = label;
      rateCell.textContent = rateLabel;
      valueCell.textContent = displayMoney(value);
      if (isSelected) row.className = "is-selected";
      row.append(name, rateCell, valueCell);
      container.appendChild(row);
    }

    function renderSensitivity() {
      const container = el("ret-sensitivity-rows");
      const baseInput = calculatorInput();
      container.replaceChildren();
      sensitivityRates(baseInput.expectedPortfolioReturn).forEach(function (scenario) {
        const result = engine.calculateRetirement(Object.assign({}, baseInput, {
          expectedPortfolioReturn: scenario.rate,
        }));
        appendComparisonRow(
          container,
          scenario.label,
          (scenario.rate * 100).toFixed(1).replace(/\.0$/, "") + "%",
          result.totalNeededToday,
          scenario.key === "selected"
        );
      });
      el("ret-sensitivity").hidden = false;
    }

    function renderHousingComparison() {
      const container = el("ret-housing-comparison-rows");
      const selectedPlan = el("ret-housing-plan").value;
      const plans = [
        { value: "rent", label: "Rent" },
        { value: "own", label: "Already own" },
        { value: "buy_now", label: "Buy now" },
        { value: "buy_retirement", label: "Buy at retirement" },
      ];
      container.replaceChildren();
      plans.forEach(function (plan) {
        const result = engine.calculateRetirement(calculatorInput(plan.value));
        const row = document.createElement("tr");
        const name = document.createElement("th");
        const today = document.createElement("td");
        const retirement = document.createElement("td");
        name.scope = "row";
        name.textContent = plan.label;
        today.textContent = displayMoney(result.totalNeededToday);
        retirement.textContent = displayMoney(result.totalCapitalAtRetirement);
        if (plan.value === selectedPlan) row.className = "is-selected";
        row.append(name, today, retirement);
        container.appendChild(row);
      });
      el("ret-housing-comparison").hidden = false;
    }

    function renderAccumulationChart(series, targetValue) {
      const figure = el("ret-accumulation-figure");
      const barsLayer = el("ret-accumulation-bars");
      const description = el("ret-accumulation-desc");
      const caption = el("ret-accumulation-caption");
      const tooltip = el("ret-accumulation-tooltip");
      const currentAge = number("ret-current-age");
      const model = accumulationChartModel({ series: series, targetValue: targetValue });
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
        const lumpY = baseline - point.lumpHeight;
        const contributionY = lumpY - point.contributionHeight;
        const label = index === 0 ? "Now" : "+" + point.year + "y";
        const yearLabel = index % labelEvery === 0 || index === count - 1
          ? '<text class="chart-axis-label" x="' + (left + index * step) + '" y="278" text-anchor="middle">' + label + '</text>'
          : "";
        const tooltipContent = accumulationTooltipContent({
          currentAge: currentAge,
          point: point,
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        });
        return '<g class="chart-year" tabindex="0" role="button" data-year-index="' + index + '" aria-label="' + tooltipContent.accessibleLabel + '" style="--year-delay:' + Math.round(index * delayStep) + 'ms">' +
          '<rect class="chart-lump" x="' + x.toFixed(2) + '" y="' + lumpY.toFixed(2) + '" width="' + barWidth.toFixed(2) + '" height="' + point.lumpHeight.toFixed(2) + '"></rect>' +
          '<rect class="chart-contribution" x="' + x.toFixed(2) + '" y="' + contributionY.toFixed(2) + '" width="' + barWidth.toFixed(2) + '" height="' + point.contributionHeight.toFixed(2) + '"></rect>' +
          yearLabel + '</g>';
      }).join("");
      const finalPoint = model.years[count - 1];
      const targetLine = el("ret-accumulation-target");
      const targetLabel = el("ret-accumulation-target-label");
      targetLine.setAttribute("y1", model.targetY.toFixed(2));
      targetLine.setAttribute("y2", model.targetY.toFixed(2));
      targetLabel.setAttribute("y", Math.max(14, model.targetY - 6).toFixed(2));
      targetLabel.textContent = "Target " + displayMoney(targetValue);
      barsLayer.innerHTML = '<line class="chart-axis" x1="22" y1="258" x2="618" y2="258"></line>' + bars;
      const yearGroups = Array.from(barsLayer.querySelectorAll(".chart-year"));
      function showTooltip(group) {
        yearGroups.forEach(function (item) { item.classList.toggle("is-active", item === group); });
        const content = accumulationTooltipContent({
          currentAge: currentAge,
          point: model.years[Number(group.dataset.yearIndex)],
          currency: selectedCurrency,
          ratesToUsd: ratesToUsd,
        });
        el("ret-tooltip-heading").textContent = content.heading;
        el("ret-tooltip-lump").textContent = content.lumpSum;
        el("ret-tooltip-contributions").textContent = content.contributions;
        el("ret-tooltip-total").textContent = content.total;
        tooltip.hidden = false;
      }
      function hideTooltip(group) {
        if (group && group.matches(":focus-visible")) return;
        if (group) group.classList.remove("is-active");
        tooltip.hidden = true;
      }
      yearGroups.forEach(function (group) {
        group.addEventListener("mouseenter", function () { showTooltip(group); });
        group.addEventListener("mouseleave", function () { hideTooltip(group); });
        group.addEventListener("focus", function () { showTooltip(group); });
        group.addEventListener("blur", function () { hideTooltip(group); });
        group.addEventListener("click", function () { showTooltip(group); });
      });
      description.textContent = "Annual portfolio progression from now to retirement, split between the lump sum invested today and inflation-adjusted monthly contributions.";
      caption.textContent = "At retirement: " + displayMoney(finalPoint.lumpSumValue) +
        " from today's lump sum and growth, plus " + displayMoney(finalPoint.contributionValue) +
        " from monthly contributions and growth.";
      figure.hidden = false;
    }

    function firstInvalidField() {
      const controls = Array.from(form.querySelectorAll("input[type=number]"));
      const invalidNumber = controls.find(isInvalidNumericControl);
      if (invalidNumber) return invalidNumber;
      return Array.from(form.querySelectorAll("input[data-money]")).find(function (control) {
        return validateMoneyControl(control);
      });
    }

    function calculate(event) {
      if (event) event.preventDefault();
      const errors = el("ret-errors");
      errors.textContent = "";
      const invalid = firstInvalidField();
      if (invalid) {
        if (event) {
          errors.textContent = "Check the highlighted numeric input and try again.";
          invalid.focus();
        }
        return false;
      }
      try {
        render(engine.calculateRetirement(calculatorInput()));
        if (event) {
          track("retirement_calculator_calculate");
          showResults();
        }
        return true;
      } catch (error) {
        errors.textContent = error instanceof Error ? error.message : "Unable to calculate this scenario.";
        errors.focus();
        return false;
      }
    }

    function updateMonthlyInvestmentPreview() {
      el("ret-monthly-investment-preview").textContent =
        "Monthly contribution: " + displayMoney(moneyNumber("ret-monthly-income") * rate("ret-income-invested-rate"));
    }

    function changePlanningCurrency(nextCurrency, shouldTrack) {
      if (!ratesToUsd[nextCurrency] || nextCurrency === selectedCurrency) return;
      const previousCurrency = selectedCurrency;
      moneyControlIds.forEach(function (id) {
        const control = el(id);
        if (!control || control.value === "") return;
        const amount = parseMoneyInput(control.value);
        if (amount === null) return;
        const converted = convertPlanningControlAmount({
          amount: amount,
          fromCurrency: previousCurrency,
          toCurrency: nextCurrency,
          ratesToUsd: ratesToUsd,
          step: planningControlConversionStep({
            controlId: id,
            controlStep: control.step,
            monthlySpendingIsAutomatic: monthlySpendingIsAutomatic,
          }),
        });
        if (converted !== null) {
          control.value = formatMoneyInputValue(converted);
          validateMoneyControl(control);
        }
      });
      selectedCurrency = nextCurrency;
      updateMonthlyInvestmentPreview();
      if (latestResult) render(latestResult);
      if (shouldTrack !== false) track("retirement_calculator_currency_change");
    }

    function scheduleCalculation() {
      updateMonthlyInvestmentPreview();
      root.clearTimeout(autoCalculationTimer);
      if (mobileQuery.matches && requestedViewMode === "editing" && editSnapshot) return;
      if (el("ret-expected-return").value === "" || firstInvalidField()) return;
      autoCalculationTimer = root.setTimeout(function () { calculate(null); }, 250);
    }

    ["ret-destination", "ret-household", "ret-housing-plan"].forEach(function (id) {
      el(id).addEventListener("change", function () {
        syncDestinationDefaults(id === "ret-destination");
        if (id === "ret-destination") track("retirement_calculator_destination_change");
      });
    });
    el("ret-currency").addEventListener("change", function () {
      changePlanningCurrency(el("ret-currency").value, true);
    });
    form.addEventListener("submit", calculate);
    form.addEventListener("input", scheduleCalculation);
    form.addEventListener("change", scheduleCalculation);
    moneyControlIds.forEach(function (id) {
      const control = el(id);
      if (!control) return;
      control.addEventListener("input", function () {
        if (id === "ret-monthly-spending") monthlySpendingIsAutomatic = false;
        validateMoneyControl(control);
      });
      control.addEventListener("blur", function () {
        formatMoneyControl(control);
        validateMoneyControl(control);
      });
    });
    el("ret-example-return").addEventListener("click", function () {
      el("ret-expected-return").value = String(illustrativeReturnExample());
      scheduleCalculation();
      track("retirement_calculator_example_return");
    });
    el("ret-save-intent-button").addEventListener("click", function () {
      el("ret-save-intent-button").hidden = true;
      el("ret-save-intent-status").hidden = false;
    });
    el("ret-adjust-plan").addEventListener("click", editPlan);
    el("ret-back-results").addEventListener("click", returnToResults);
    if (typeof mobileQuery.addEventListener === "function") {
      mobileQuery.addEventListener("change", handleViewportChange);
    }
    ["ret-current-location", "ret-current-monthly-spending"].forEach(function (id) {
      el(id).addEventListener("input", function () { renderCurrentCostComparison(); });
    });
    syncDestinationDefaults(true);
    if (initialCurrency !== "USD") {
      el("ret-currency").value = initialCurrency;
      changePlanningCurrency(initialCurrency, false);
    }
    updateMonthlyInvestmentPreview();
    initDestinationCostSidecar();
    applyCalculatorView();
    track("retirement_calculator_open");
  }

  function retirementPrefill(queryString) {
    const params = new URLSearchParams(String(queryString || ""));
    const destinationValue = params.get("destination") || "";
    const householdValue = params.get("household") || "";
    const housingValue = params.get("housing") || "";
    return {
      destination: /^[a-z0-9-]+$/.test(destinationValue) ? destinationValue : "",
      household: new Set(["single", "couple"]).has(householdValue) ? householdValue : "",
      housing: new Set(["rent", "own", "buy_now", "buy_retirement"]).has(housingValue) ? housingValue : "",
    };
  }

  return {
    convertPlanningAmount: convertPlanningAmount,
    convertPlanningControlAmount: convertPlanningControlAmount,
    planningControlConversionStep: planningControlConversionStep,
    preferredPlanningCurrency: preferredPlanningCurrency,
    retirementCalculatorViewState: retirementCalculatorViewState,
    retirementCalculatorViewportAction: retirementCalculatorViewportAction,
    retirementCalculatorViewportResolution: retirementCalculatorViewportResolution,
    parseMoneyInput: parseMoneyInput,
    formatMoneyInputValue: formatMoneyInputValue,
    isInvalidMoneyInput: isInvalidMoneyInput,
    formatPlanningMoney: formatPlanningMoney,
    annualSpendingFromMonthly: annualSpendingFromMonthly,
    roundToNearestHundred: roundToNearestHundred,
    illustrativeReturnExample: illustrativeReturnExample,
    currentCostComparison: currentCostComparison,
    retirementTargetComparison: retirementTargetComparison,
    annualBenchmark: annualBenchmark,
    rankDestinationCosts: rankDestinationCosts,
    usesPropertyBudget: usesPropertyBudget,
    housingGuidance: housingGuidance,
    housingExpenseLabels: housingExpenseLabels,
    accumulationChartModel: accumulationChartModel,
    sensitivityRates: sensitivityRates,
    planningSummary: planningSummary,
    accumulationTooltipContent: accumulationTooltipContent,
    isInvalidNumericControl: isInvalidNumericControl,
    isNegativeRate: isNegativeRate,
    isBenchmarkPanelHidden: isBenchmarkPanelHidden,
    partitionBenchmarkRows: partitionBenchmarkRows,
    retirementPrefill: retirementPrefill,
    initRetirementBenchmarkTable: initRetirementBenchmarkTable,
    initRetirementCalculator: initRetirementCalculator,
  };
});
