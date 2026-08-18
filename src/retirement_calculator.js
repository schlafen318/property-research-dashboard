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
    if (yearsToRetirement <= 0) throw new Error("Retirement age must exceed current age");

    const horizonYears = finiteNonNegative(input.horizonYears, "Retirement horizon");
    if (horizonYears === 0) throw new Error("Retirement horizon must be positive");
    const generalInflation = boundedRate(input.generalInflation, "General inflation", 0.15);
    const propertyInflation = boundedRate(input.propertyInflation, "Property inflation", 0.15);
    const acquisitionCostRate = boundedRate(input.acquisitionCostRate, "Acquisition cost rate", 0.25);
    const emergencyReserveMonths = finiteNonNegative(input.emergencyReserveMonths, "Emergency reserve months");
    const expectedPortfolioReturn = boundedExpectedReturn(input.expectedPortfolioReturn);

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
      const expenses = projectedExpenseTotal(input.expenseCategories, projectionYears);
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
    const impliedFirstYearWithdrawal = liquidPortfolio > 0 ? fundingGap / liquidPortfolio : null;
    const todayDollarRetirementCapital = retirementCapital / Math.pow(1 + generalInflation, yearsToRetirement);

    return {
      yearsToRetirement: yearsToRetirement,
      firstYearExpenses: firstYearExpenses,
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
      impliedFirstYearWithdrawal: impliedFirstYearWithdrawal,
      todayDollarRetirementCapital: todayDollarRetirementCapital,
    };
  }

  return {
    calculateRetirement: calculateRetirement,
  };
});
