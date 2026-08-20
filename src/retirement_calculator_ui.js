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

  function planningSummary(result) {
    const investment = money.format(Number(result.investmentNeededToday));
    const contribution = money.format(Number(result.monthlyContributionToday));
    const home = Number(result.homePurchaseNeededToday);
    if (home > 0) {
      return "Invest " + investment + " today and " + contribution +
        " per month for retirement, plus " + money.format(home) + " for the home purchase.";
    }
    return "Invest " + investment + " today and " + contribution +
      " per month to fund this retirement plan.";
  }

  function accumulationTooltipContent(input) {
    const point = input.point;
    const projectedAge = Number(input.currentAge) + Number(point.year);
    const lumpSum = money.format(Number(point.lumpSumValue));
    const contributions = money.format(Number(point.contributionValue));
    const total = money.format(Number(point.totalValue));
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
    let benchmarkValue = 0;
    let autoCalculationTimer = null;
    let hasTrackedResult = false;

    function selectedRecord() {
      return byId[el("ret-destination").value];
    }

    function syncDestinationDefaults(resetPropertyBudget) {
      const record = selectedRecord();
      if (!record) return;
      const profile = record.profiles[el("ret-household").value];
      const plan = el("ret-housing-plan").value;
      const expenseLabels = housingExpenseLabels(plan);
      benchmarkValue = annualBenchmark({ profile: profile, plan: plan });
      el("ret-monthly-spending").value = String(Math.round(benchmarkValue / 12));
      el("ret-monthly-spending-label").textContent = expenseLabels.input;
      el("ret-first-expenses-label").textContent = expenseLabels.result;
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
      context.textContent = el("ret-household").selectedOptions[0].textContent + " · Monthly USD " +
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
        button.setAttribute("aria-label", "Select " + row.name + ", " + money.format(row.monthlyCost) +
          " per month, rank " + (index + 1) + " of " + rows.length);
        if (row.destinationId === currentId) {
          button.classList.add("is-current");
          button.setAttribute("aria-current", "true");
        }
        heading.className = "cost-row-heading";
        name.textContent = (index + 1) + ". " + row.name;
        amount.textContent = money.format(row.monthlyCost) + "/mo";
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

    function calculatorInput(planOverride) {
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
        monthlyIncomeBeforeRetirement: number("ret-monthly-income"),
        incomeInvestedRate: rate("ret-income-invested-rate"),
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
      el("ret-detailed-projection").hidden = false;
      el("ret-plan-summary").textContent = planningSummary(result);
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
      el("ret-result-assumptions").textContent =
        "Data " + payload.as_of + " · " + record.confidence.overall + " confidence · " +
        "uses the same expected return every year. Actual return order and market losses can materially change the outcome. " +
        "Planning estimate only; not financial, tax, legal, immigration, healthcare, or investment advice.";
      el("ret-save-action").hidden = false;
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
      valueCell.textContent = money.format(value);
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
        today.textContent = money.format(result.totalNeededToday);
        retirement.textContent = money.format(result.totalCapitalAtRetirement);
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
        const tooltipContent = accumulationTooltipContent({ currentAge: currentAge, point: point });
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
      targetLabel.textContent = "Target " + money.format(targetValue);
      barsLayer.innerHTML = '<line class="chart-axis" x1="22" y1="258" x2="618" y2="258"></line>' + bars;
      const yearGroups = Array.from(barsLayer.querySelectorAll(".chart-year"));
      function showTooltip(group) {
        yearGroups.forEach(function (item) { item.classList.toggle("is-active", item === group); });
        const content = accumulationTooltipContent({
          currentAge: currentAge,
          point: model.years[Number(group.dataset.yearIndex)],
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
      caption.textContent = "At retirement: " + money.format(finalPoint.lumpSumValue) +
        " from today's lump sum and growth, plus " + money.format(finalPoint.contributionValue) +
        " from monthly contributions and growth.";
      figure.hidden = false;
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
        if (event) {
          errors.textContent = "Check the highlighted numeric input and try again.";
          invalid.focus();
        }
        return;
      }
      try {
        render(engine.calculateRetirement(calculatorInput()));
        if (event) track("retirement_calculator_calculate");
      } catch (error) {
        errors.textContent = error instanceof Error ? error.message : "Unable to calculate this scenario.";
        errors.focus();
      }
    }

    function updateMonthlyInvestmentPreview() {
      el("ret-monthly-investment-preview").textContent =
        "Monthly contribution: " + money.format(number("ret-monthly-income") * rate("ret-income-invested-rate"));
    }

    function scheduleCalculation() {
      updateMonthlyInvestmentPreview();
      root.clearTimeout(autoCalculationTimer);
      if (el("ret-expected-return").value === "" || firstInvalidField()) return;
      autoCalculationTimer = root.setTimeout(function () { calculate(null); }, 250);
    }

    ["ret-destination", "ret-household", "ret-housing-plan"].forEach(function (id) {
      el(id).addEventListener("change", function () {
        syncDestinationDefaults(id === "ret-destination");
        if (id === "ret-destination") track("retirement_calculator_destination_change");
      });
    });
    form.addEventListener("submit", calculate);
    form.addEventListener("input", scheduleCalculation);
    form.addEventListener("change", scheduleCalculation);
    el("ret-save-intent-button").addEventListener("click", function () {
      el("ret-save-intent-button").hidden = true;
      el("ret-save-intent-status").hidden = false;
    });
    syncDestinationDefaults(true);
    updateMonthlyInvestmentPreview();
    initDestinationCostSidecar();
    track("retirement_calculator_open");
  }

  return {
    annualSpendingFromMonthly: annualSpendingFromMonthly,
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
    initRetirementBenchmarkTable: initRetirementBenchmarkTable,
    initRetirementCalculator: initRetirementCalculator,
  };
});
