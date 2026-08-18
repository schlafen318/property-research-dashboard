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
  const presetYields = { "income": 0.03, "balanced": 0.02, "growth": 0.01 };

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

  function housingGuidance(plan) {
    if (plan === "rent") return "Includes rent and other living costs.";
    if (plan === "own") return "Includes owner running costs, with no new home purchase.";
    return "Includes owner running costs after purchase, not rent. Enter the home purchase budget separately.";
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
      el("ret-property-field").hidden = plan !== "buy";
      el("ret-property-budget").disabled = plan !== "buy";
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
      const override = el("ret-withdrawal-rate").value.trim();
      const input = {
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
        portfolioCashYield: rate("ret-cash-yield"),
      };
      if (override !== "") input.withdrawalRateOverride = Number(override) / 100;
      return input;
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
        portfolio_style: el("ret-income-preset").value,
      };
    }

    function track(name) {
      if (root.GHA && typeof root.GHA.track === "function") root.GHA.track(name, trackingContext());
    }

    function render(result) {
      const record = selectedRecord();
      setMoney("ret-total-capital", result.totalCapital);
      setMoney("ret-liquid-portfolio", result.liquidPortfolio);
      setMoney("ret-property-capital", result.propertyCapital);
      setMoney("ret-emergency-reserve", result.emergencyReserve);
      setMoney("ret-today-total", result.todayDollarTotal);
      setMoney("ret-first-expenses", result.firstYearExpenses);
      setMoney("ret-outside-income", result.outsideIncome);
      setMoney("ret-funding-gap", result.fundingGap);
      setMoney("ret-cash-income", result.portfolioCashIncome);
      setMoney("ret-asset-sales", result.assetSales);
      el("ret-result-rate").textContent = (result.withdrawalRate * 100).toFixed(2).replace(/\.00$/, "") + "%";
      el("ret-result-status").textContent = record.name + " · " + el("ret-household").selectedOptions[0].textContent + " · " + result.yearsToRetirement + " years to retirement";
      const lowerRate = Math.max(0.03, result.withdrawalRate - 0.005);
      const upperRate = Math.min(0.04, result.withdrawalRate + 0.005);
      el("ret-result-assumptions").textContent =
        "Data " + payload.as_of + " · " + record.confidence.overall + " confidence · " +
        "rate sensitivity " + (lowerRate * 100).toFixed(2) + "%–" + (upperRate * 100).toFixed(2) +
        "%. Planning estimate only; not financial, tax, legal, immigration, healthcare, or investment advice.";
    }

    function firstInvalidField() {
      const controls = Array.from(form.querySelectorAll("input[type=number]"));
      return controls.find(function (control) {
        return control.value === "" && control.id !== "ret-withdrawal-rate" || !control.checkValidity();
      });
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
    el("ret-income-preset").addEventListener("change", function () {
      el("ret-cash-yield").value = String(presetYields[this.value] * 100);
    });
    form.addEventListener("submit", calculate);
    syncDestinationDefaults(true);
    track("retirement_calculator_open");
  }

  return {
    annualSpendingFromMonthly: annualSpendingFromMonthly,
    annualBenchmark: annualBenchmark,
    housingGuidance: housingGuidance,
    initRetirementCalculator: initRetirementCalculator,
  };
});
