(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementCalculator = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const HOUSING_PLANS = new Set(["rent", "own", "buy"]);

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

  function guidedWithdrawalRate(horizonYears) {
    const horizon = finiteNonNegative(horizonYears, "Retirement horizon");
    if (horizon === 0) throw new Error("Retirement horizon must be positive");
    if (horizon <= 25) return 0.04;
    if (horizon <= 30) return 0.035;
    if (horizon <= 35) return 0.0325;
    return 0.03;
  }

  function project(value, rate, years) {
    return value * Math.pow(1 + rate, years);
  }

  function calculateRetirement(input) {
    if (!input || typeof input !== "object") throw new Error("Calculator input is required");

    const currentAge = finiteNonNegative(input.currentAge, "Current age");
    const retirementAge = finiteNonNegative(input.retirementAge, "Retirement age");
    const yearsToRetirement = retirementAge - currentAge;
    if (yearsToRetirement <= 0) throw new Error("Retirement age must exceed current age");

    const horizonYears = finiteNonNegative(input.horizonYears, "Retirement horizon");
    const generalInflation = boundedRate(input.generalInflation, "General inflation", 0.15);
    const propertyInflation = boundedRate(input.propertyInflation, "Property inflation", 0.15);
    const acquisitionCostRate = boundedRate(input.acquisitionCostRate, "Acquisition cost rate", 0.25);
    const emergencyReserveMonths = finiteNonNegative(input.emergencyReserveMonths, "Emergency reserve months");
    const portfolioCashYield = boundedRate(input.portfolioCashYield, "Portfolio cash yield", 0.15);

    if (!HOUSING_PLANS.has(input.housingPlan)) throw new Error("Housing plan must be rent, own, or buy");
    if (!Array.isArray(input.expenseCategories) || input.expenseCategories.length === 0) {
      throw new Error("At least one expense category is required");
    }
    if (!Array.isArray(input.incomeStreams)) throw new Error("Income streams must be an array");

    const firstYearExpenses = input.expenseCategories.reduce(function (total, category) {
      const amount = finiteNonNegative(category.amount, "Expense amount");
      const rate = boundedRate(category.inflationRate, "Expense inflation", 0.15);
      return total + project(amount, rate, yearsToRetirement);
    }, 0);

    const outsideIncome = input.incomeStreams.reduce(function (total, stream) {
      const amount = finiteNonNegative(stream.amount, "Income amount");
      const rate = boundedRate(stream.inflationRate, "Income inflation", 0.15);
      return total + (stream.indexed ? project(amount, rate, yearsToRetirement) : amount);
    }, 0);

    let withdrawalRate = guidedWithdrawalRate(horizonYears);
    if (input.withdrawalRateOverride !== undefined && input.withdrawalRateOverride !== null) {
      withdrawalRate = Number(input.withdrawalRateOverride);
      if (!Number.isFinite(withdrawalRate) || withdrawalRate < 0.03 || withdrawalRate > 0.04) {
        throw new Error("Withdrawal rate override must be between 3% and 4%");
      }
    }

    const fundingGap = Math.max(0, firstYearExpenses - outsideIncome);
    const liquidPortfolio = fundingGap / withdrawalRate;
    const propertyPrice = finiteNonNegative(input.propertyPrice, "Property price");
    const propertyCapital = input.housingPlan === "buy"
      ? project(propertyPrice, propertyInflation, yearsToRetirement) * (1 + acquisitionCostRate)
      : 0;
    const emergencyReserve = firstYearExpenses / 12 * emergencyReserveMonths;
    const totalCapital = liquidPortfolio + propertyCapital + emergencyReserve;
    const portfolioCashIncome = Math.min(fundingGap, liquidPortfolio * portfolioCashYield);
    const assetSales = Math.max(0, fundingGap - portfolioCashIncome);
    const todayDollarTotal = totalCapital / Math.pow(1 + generalInflation, yearsToRetirement);

    return {
      yearsToRetirement: yearsToRetirement,
      firstYearExpenses: firstYearExpenses,
      outsideIncome: outsideIncome,
      fundingGap: fundingGap,
      withdrawalRate: withdrawalRate,
      liquidPortfolio: liquidPortfolio,
      propertyCapital: propertyCapital,
      emergencyReserve: emergencyReserve,
      totalCapital: totalCapital,
      portfolioCashIncome: portfolioCashIncome,
      assetSales: assetSales,
      todayDollarTotal: todayDollarTotal,
    };
  }

  return {
    guidedWithdrawalRate: guidedWithdrawalRate,
    calculateRetirement: calculateRetirement,
  };
});
