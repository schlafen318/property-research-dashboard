(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementCalculator = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const HOUSING_PLANS = new Set(["rent", "own", "buy_now", "buy_retirement"]);

  function finiteNonNegative(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number) || number < 0) {
      throw new Error(label + " must be a finite non-negative number");
    }
    return number;
  }

  function boundedRate(value, label, maximum) {
    const rate = finiteNonNegative(value, label);
    if (rate > maximum) throw new Error(label + " exceeds the allowed range");
    return rate;
  }

  function project(value, rate, years) {
    return value * Math.pow(1 + rate, years);
  }

  function normalizeFloatingPoint(value) {
    const nearestInteger = Math.round(value);
    return Math.abs(value - nearestInteger) < 1e-9 ? nearestInteger : value;
  }

  function boundedExpectedReturn(value) {
    if (value === null || value === undefined || value === "") {
      throw new Error("Expected portfolio return is required");
    }
    const rate = Number(value);
    if (!Number.isFinite(rate) || rate < -0.05 || rate > 0.15) {
      throw new Error("Expected portfolio return must be between -5% and 15%");
    }
    return rate;
  }

  function normalizedReturnBasis(input) {
    const basis = input.returnBasis === undefined || input.returnBasis === null || input.returnBasis === ""
      ? "unspecified"
      : String(input.returnBasis);
    if (!new Set(["unspecified", "after_fees", "after_fees_and_tax", "gross"]).has(basis)) {
      throw new Error("Return basis is invalid");
    }
    return basis;
  }

  function normalizedTaxMode(input, returnBasis) {
    const mode = input.taxMode === undefined || input.taxMode === null || input.taxMode === ""
      ? (returnBasis === "after_fees_and_tax" ? "user_after_tax" : "unspecified")
      : String(input.taxMode);
    if (!new Set(["unspecified", "user_after_tax", "destination_estimate"]).has(mode)) {
      throw new Error("Tax mode must be unspecified, user_after_tax or destination_estimate");
    }
    return mode;
  }

  function annualTaxExpenses(input) {
    const returnBasis = normalizedReturnBasis(input);
    const mode = normalizedTaxMode(input, returnBasis);
    const supplied = input.annualTaxExpenses;
    if (mode === "destination_estimate" && (supplied === undefined || supplied === null || supplied === "")) {
      throw new Error("Destination tax estimate requires annualTaxExpenses from a TaxScenario");
    }
    const amount = supplied === undefined || supplied === null || supplied === ""
      ? 0
      : finiteNonNegative(supplied, "Annual tax expenses");
    if (amount > 0 && returnBasis !== "after_fees_and_tax") {
      throw new Error("Tax-adjusted results require returnBasis after_fees_and_tax");
    }
    if (mode === "destination_estimate" && returnBasis !== "after_fees_and_tax") {
      throw new Error("Destination tax estimate requires returnBasis after_fees_and_tax");
    }
    if (mode === "user_after_tax" && returnBasis !== "after_fees_and_tax") {
      throw new Error("User after-tax mode requires returnBasis after_fees_and_tax");
    }
    return {
      mode: mode,
      amount: amount,
      returnBasis: returnBasis,
    };
  }

  function projectedExpenseTotal(categories, years) {
    return categories.reduce(function (total, category) {
      const amount = finiteNonNegative(category.amount, "Expense amount");
      const inflation = boundedRate(category.inflationRate, "Expense inflation", 0.15);
      return total + project(amount, inflation, years);
    }, 0);
  }

  function projectedIncomeTotal(streams, years) {
    return streams.reduce(function (total, stream) {
      const amount = finiteNonNegative(stream.amount, "Income amount");
      const inflation = boundedRate(stream.inflationRate, "Income inflation", 0.15);
      return total + (stream.indexed ? project(amount, inflation, years) : amount);
    }, 0);
  }

  function calculateRetirement(input) {
    if (!input || typeof input !== "object") throw new Error("Calculator input is required");

    const currentAge = finiteNonNegative(input.currentAge, "Current age");
    const retirementAge = finiteNonNegative(input.retirementAge, "Retirement age");
    const yearsToRetirement = retirementAge - currentAge;
    if (yearsToRetirement < 0 || (yearsToRetirement === 0 && input.retirementBeginsNow !== true)) {
      throw new Error("Retirement age must exceed current age");
    }

    const horizonYears = finiteNonNegative(input.horizonYears, "Retirement horizon");
    if (horizonYears === 0) throw new Error("Retirement horizon must be positive");
    const generalInflation = boundedRate(input.generalInflation, "General inflation", 0.15);
    const propertyInflation = boundedRate(input.propertyInflation, "Property inflation", 0.15);
    const acquisitionCostRate = boundedRate(input.acquisitionCostRate, "Acquisition cost rate", 0.25);
    const emergencyReserveMonths = finiteNonNegative(input.emergencyReserveMonths, "Emergency reserve months");
    const expectedPortfolioReturn = boundedExpectedReturn(input.expectedPortfolioReturn);
    const monthlyIncomeBeforeRetirement = finiteNonNegative(
      input.monthlyIncomeBeforeRetirement,
      "Monthly income before retirement"
    );
    const incomeInvestedRate = boundedRate(input.incomeInvestedRate, "Income invested rate", 1);
    const tax = annualTaxExpenses(input);

    if (!HOUSING_PLANS.has(input.housingPlan)) {
      throw new Error("Housing plan must be rent, own, buy_now, or buy_retirement");
    }
    if (!Array.isArray(input.expenseCategories) || input.expenseCategories.length === 0) {
      throw new Error("At least one expense category is required");
    }
    if (!Array.isArray(input.incomeStreams)) throw new Error("Income streams must be an array");

    const annualFundingGaps = [];
    let firstYearExpenses = 0;
    let outsideIncome = 0;
    for (let year = 0; year < horizonYears; year += 1) {
      const projectionYears = yearsToRetirement + year;
      const taxExpenses = project(tax.amount, generalInflation, projectionYears);
      const expenses = projectedExpenseTotal(input.expenseCategories, projectionYears) + taxExpenses;
      const income = projectedIncomeTotal(input.incomeStreams, projectionYears);
      if (year === 0) {
        firstYearExpenses = expenses;
        outsideIncome = income;
      }
      annualFundingGaps.push(normalizeFloatingPoint(Math.max(0, expenses - income)));
    }

    const liquidPortfolio = annualFundingGaps.reduce(function (total, gap, year) {
      return total + gap / Math.pow(1 + expectedPortfolioReturn, year);
    }, 0);
    const fundingGap = annualFundingGaps[0] || 0;
    const propertyPrice = finiteNonNegative(input.propertyPrice, "Property price");
    const emergencyReserve = firstYearExpenses / 12 * emergencyReserveMonths;
    const retirementCapital = liquidPortfolio + emergencyReserve;
    let propertyCapital = 0;
    let propertyTiming = "none";
    let combinedRetirementCapital = retirementCapital;
    if (input.housingPlan === "buy_now") {
      propertyCapital = propertyPrice * (1 + acquisitionCostRate);
      propertyTiming = "today";
      combinedRetirementCapital = null;
    } else if (input.housingPlan === "buy_retirement") {
      propertyCapital = project(propertyPrice, propertyInflation, yearsToRetirement) * (1 + acquisitionCostRate);
      propertyTiming = "retirement";
      combinedRetirementCapital = retirementCapital + propertyCapital;
    }
    const totalCapitalAtRetirement = combinedRetirementCapital === null
      ? retirementCapital
      : combinedRetirementCapital;
    const monthsToRetirement = yearsToRetirement * 12;
    const monthlyPortfolioReturn = Math.pow(1 + expectedPortfolioReturn, 1 / 12) - 1;
    const monthlyContributionToday = monthlyIncomeBeforeRetirement * incomeInvestedRate;
    let contributionValueAtRetirement = 0;
    for (let month = 0; month < monthsToRetirement; month += 1) {
      const completedYears = Math.floor(month / 12);
      const monthlyContribution = monthlyContributionToday * Math.pow(1 + generalInflation, completedYears);
      contributionValueAtRetirement = contributionValueAtRetirement * (1 + monthlyPortfolioReturn) + monthlyContribution;
    }
    const retirementCapitalNotFundedByContributions = Math.max(
      0,
      totalCapitalAtRetirement - contributionValueAtRetirement
    );
    const investmentNeededToday = retirementCapitalNotFundedByContributions /
      Math.pow(1 + expectedPortfolioReturn, yearsToRetirement);
    const homePurchaseNeededToday = propertyTiming === "today" ? propertyCapital : 0;
    const totalNeededToday = investmentNeededToday + homePurchaseNeededToday;
    const annualAccumulation = [{
      year: 0,
      lumpSumValue: investmentNeededToday,
      contributionValue: 0,
      totalValue: investmentNeededToday,
    }];
    let lumpSumValue = investmentNeededToday;
    let contributionValue = 0;
    for (let month = 0; month < monthsToRetirement; month += 1) {
      const completedYears = Math.floor(month / 12);
      const monthlyContribution = monthlyContributionToday * Math.pow(1 + generalInflation, completedYears);
      lumpSumValue *= 1 + monthlyPortfolioReturn;
      contributionValue = contributionValue * (1 + monthlyPortfolioReturn) + monthlyContribution;
      if ((month + 1) % 12 === 0) {
        annualAccumulation.push({
          year: (month + 1) / 12,
          lumpSumValue: normalizeFloatingPoint(lumpSumValue),
          contributionValue: normalizeFloatingPoint(contributionValue),
          totalValue: normalizeFloatingPoint(lumpSumValue + contributionValue),
        });
      }
    }
    const impliedFirstYearWithdrawal = liquidPortfolio > 0 ? fundingGap / liquidPortfolio : null;
    const netReturnAfterWithdrawal = impliedFirstYearWithdrawal === null
      ? null
      : expectedPortfolioReturn - impliedFirstYearWithdrawal;
    const todayDollarRetirementCapital = retirementCapital / Math.pow(1 + generalInflation, yearsToRetirement);

    return {
      yearsToRetirement: yearsToRetirement,
      firstYearExpenses: firstYearExpenses,
      annualTaxExpenses: project(tax.amount, generalInflation, yearsToRetirement),
      taxMode: tax.mode,
      returnBasis: tax.returnBasis,
      outsideIncome: outsideIncome,
      fundingGap: fundingGap,
      annualFundingGaps: annualFundingGaps,
      expectedPortfolioReturn: expectedPortfolioReturn,
      liquidPortfolio: liquidPortfolio,
      propertyCapital: propertyCapital,
      propertyTiming: propertyTiming,
      emergencyReserve: emergencyReserve,
      retirementCapital: retirementCapital,
      combinedRetirementCapital: combinedRetirementCapital,
      totalCapitalAtRetirement: totalCapitalAtRetirement,
      monthlyContributionToday: monthlyContributionToday,
      contributionValueAtRetirement: normalizeFloatingPoint(contributionValueAtRetirement),
      annualAccumulation: annualAccumulation,
      investmentNeededToday: investmentNeededToday,
      homePurchaseNeededToday: homePurchaseNeededToday,
      totalNeededToday: totalNeededToday,
      impliedFirstYearWithdrawal: impliedFirstYearWithdrawal,
      netReturnAfterWithdrawal: netReturnAfterWithdrawal,
      todayDollarRetirementCapital: todayDollarRetirementCapital,
    };
  }

  return {
    calculateRetirement: calculateRetirement,
    calculateRetirementTarget: calculateRetirement,
  };
});
