(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementCalculatorUI = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

  function annualSpendingFromMonthly(monthlySpending) {
    return Number(monthlySpending) * 12;
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
    let benchmarkValue = 0;

    function selectedRecord() {
      return byId[el("ret-destination").value];
    }

    function syncDestinationDefaults(resetPropertyBudget) {
      const record = selectedRecord();
      if (!record) return;
      const profile = record.profiles[el("ret-household").value];
      const plan = el("ret-housing-plan").value;
      benchmarkValue = annualBenchmark({ profile: profile, plan: plan });
      el("ret-monthly-spending").value = String(Math.round(benchmarkValue / 12));
      el("ret-housing-guidance").textContent = housingGuidance(plan);
      el("ret-property-field").hidden = !usesPropertyBudget(plan);
      el("ret-property-budget").disabled = !usesPropertyBudget(plan);
      if (resetPropertyBudget) {
        el("ret-property-budget").value = String(Math.round(Number(record.property.representative_price_usd)));
      }
      el("ret-general-inflation").value = String(record.inflation.general * 100);
      el("ret-healthcare-inflation").value = String(record.inflation.healthcare * 100);
      el("ret-property-inflation").value = String(record.inflation.property * 100);
    }

    function expenseCategories(record, profile, plan) {
      const generalRate = rate("ret-general-inflation");
      const healthcareRate = rate("ret-healthcare-inflation");
      const propertyRate = rate("ret-property-inflation");
      const annualSpending = annualSpendingFromMonthly(number("ret-monthly-spending"));
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

    function calculatorInput() {
      const record = selectedRecord();
      if (!record) throw new Error("Choose a destination with available cost data");
      const household = el("ret-household").value;
      const profile = record.profiles[household];
      const plan = el("ret-housing-plan").value;
      const generalRate = rate("ret-general-inflation");
      return {
        currentAge: number("ret-current-age"),
        retirementAge: number("ret-retirement-age"),
        horizonYears: number("ret-horizon"),
        expenseCategories: expenseCategories(record, profile, plan),
        incomeStreams: [
          { amount: number("ret-pension"), indexed: el("ret-pension-indexed").checked, inflationRate: generalRate },
          { amount: number("ret-other-income"), indexed: el("ret-other-indexed").checked, inflationRate: generalRate },
          { amount: number("ret-rental-income"), indexed: el("ret-rental-indexed").checked, inflationRate: generalRate },
        ],
        housingPlan: plan,
        propertyPrice: number("ret-property-budget"),
        propertyInflation: rate("ret-property-inflation"),
        acquisitionCostRate: Number(record.property.acquisition_cost_rate),
        generalInflation: generalRate,
        emergencyReserveMonths: number("ret-reserve-months"),
        expectedPortfolioReturn: rate("ret-expected-return"),
      };
    }

    function setMoney(id, value) {
      el(id).textContent = money.format(value);
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

    function render(result) {
      const record = selectedRecord();
      setMoney("ret-total-today", result.totalNeededToday);
      setMoney("ret-invest-today", result.investmentNeededToday);
      setMoney("ret-home-today", result.homePurchaseNeededToday);
      setMoney("ret-total-retirement", result.totalCapitalAtRetirement);
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
        : "No home purchase today";
      el("ret-property-retirement-label").textContent = result.propertyTiming === "retirement"
        ? "Home purchase at retirement"
        : "No home purchase at retirement";
      el("ret-result-status").textContent = record.name + " · " + el("ret-household").selectedOptions[0].textContent + " · " + result.yearsToRetirement + " years to retirement";
      el("ret-result-assumptions").textContent =
        "Data " + payload.as_of + " · " + record.confidence.overall + " confidence · " +
        "uses the same expected return every year. Actual return order and market losses can materially change the outcome. " +
        "Planning estimate only; not financial, tax, legal, immigration, healthcare, or investment advice.";
    }

    function firstInvalidField() {
      const controls = Array.from(form.querySelectorAll("input[type=number]"));
      return controls.find(isInvalidNumericControl);
    }

    function calculate(event) {
      if (event) event.preventDefault();
      const errors = el("ret-errors");
      errors.textContent = "";
      const invalid = firstInvalidField();
      if (invalid) {
        errors.textContent = "Check the highlighted numeric input and try again.";
        invalid.focus();
        return;
      }
      try {
        render(engine.calculateRetirement(calculatorInput()));
        track("retirement_calculator_calculate");
      } catch (error) {
        errors.textContent = error instanceof Error ? error.message : "Unable to calculate this scenario.";
        errors.focus();
      }
    }

    ["ret-destination", "ret-household", "ret-housing-plan"].forEach(function (id) {
      el(id).addEventListener("change", function () {
        syncDestinationDefaults(id === "ret-destination");
        if (id === "ret-destination") track("retirement_calculator_destination_change");
      });
    });
    form.addEventListener("submit", calculate);
    syncDestinationDefaults(true);
    track("retirement_calculator_open");
  }

  return {
    annualSpendingFromMonthly: annualSpendingFromMonthly,
    annualBenchmark: annualBenchmark,
    usesPropertyBudget: usesPropertyBudget,
    housingGuidance: housingGuidance,
    isInvalidNumericControl: isInvalidNumericControl,
    isNegativeRate: isNegativeRate,
    isBenchmarkPanelHidden: isBenchmarkPanelHidden,
    partitionBenchmarkRows: partitionBenchmarkRows,
    initRetirementBenchmarkTable: initRetirementBenchmarkTable,
    initRetirementCalculator: initRetirementCalculator,
  };
});
