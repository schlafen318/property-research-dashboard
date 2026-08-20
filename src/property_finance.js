(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAPropertyFinance = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  function finite(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number)) throw new Error(label + " must be finite");
    return number;
  }

  function nonNegative(value, label) {
    const number = finite(value, label);
    if (number < 0) throw new Error(label + " must be non-negative");
    return number;
  }

  function rate(value, label, maximum) {
    const number = nonNegative(value, label);
    if (number > maximum) throw new Error(label + " exceeds the allowed range");
    return number;
  }

  function monthlyMortgagePayment(input) {
    const principal = nonNegative(input.principal, "Mortgage principal");
    const annualRate = rate(input.annualRate, "Mortgage rate", 0.25);
    const termMonths = Math.round(nonNegative(input.termMonths, "Mortgage term"));
    if (termMonths <= 0) throw new Error("Mortgage term must be positive");
    if (principal === 0) return 0;
    if (annualRate === 0) return principal / termMonths;
    const monthlyRate = annualRate / 12;
    return principal * monthlyRate / (1 - Math.pow(1 + monthlyRate, -termMonths));
  }

  function amortizeMortgage(input) {
    const principal = nonNegative(input.principal, "Mortgage principal");
    const annualRate = rate(input.annualRate, "Mortgage rate", 0.25);
    const termMonths = Math.round(nonNegative(input.termMonths, "Mortgage term"));
    const elapsedMonths = Math.min(
      termMonths,
      Math.round(nonNegative(input.elapsedMonths, "Elapsed mortgage months"))
    );
    const monthlyPayment = monthlyMortgagePayment({
      principal: principal,
      annualRate: annualRate,
      termMonths: termMonths,
    });
    const monthlyRate = annualRate / 12;
    let balance = principal;
    let interestPaid = 0;
    let principalPaid = 0;
    for (let month = 0; month < elapsedMonths && balance > 0; month += 1) {
      const interest = balance * monthlyRate;
      const principalPart = Math.min(balance, monthlyPayment - interest);
      interestPaid += interest;
      principalPaid += principalPart;
      balance = Math.max(0, balance - principalPart);
    }
    return {
      monthlyPayment: monthlyPayment,
      remainingBalance: balance,
      interestPaid: interestPaid,
      principalPaid: principalPaid,
    };
  }

  function evaluateBuyNow(input) {
    if (!input || typeof input !== "object") throw new Error("Property finance input is required");
    const currentAge = nonNegative(input.currentAge, "Current age");
    const retirementAge = nonNegative(input.retirementAge, "Retirement age");
    const monthsToRetirement = Math.round((retirementAge - currentAge) * 12);
    if (monthsToRetirement <= 0) throw new Error("Retirement age must exceed current age");

    const totalLiquidCapital = nonNegative(input.totalLiquidCapital, "Total liquid capital");
    const maximumPropertyAllocation = nonNegative(input.maximumPropertyAllocation, "Maximum property allocation");
    const propertyPrice = nonNegative(input.propertyPrice, "Property price");
    const acquisitionCostRate = rate(input.acquisitionCostRate, "Acquisition cost rate", 0.25);
    const propertyInflation = rate(input.propertyInflation, "Property inflation", 0.15);
    const ownerCostInflation = rate(input.ownerCostInflation, "Owner cost inflation", 0.15);
    const generalInflation = rate(input.generalInflation, "General inflation", 0.15);
    const expectedPortfolioReturn = finite(input.expectedPortfolioReturn, "Expected portfolio return");
    if (expectedPortfolioReturn < -0.05 || expectedPortfolioReturn > 0.15) {
      throw new Error("Expected portfolio return must be between -5% and 15%");
    }
    const monthlyPortfolioContribution = nonNegative(
      input.monthlyPortfolioContribution,
      "Monthly portfolio contribution"
    );
    const annualOwnerCosts = nonNegative(input.annualOwnerCosts, "Annual owner costs");
    const grossRentalYield = rate(input.grossRentalYield, "Gross rental yield", 0.30);
    const vacancyRate = rate(input.vacancyRate, "Vacancy rate", 1);
    const operatingCostRate = rate(input.operatingCostRate, "Operating cost rate", 1);
    const requestedLtv = rate(input.requestedLtv, "Requested loan-to-value", 1);
    const annualMortgageRate = rate(input.annualMortgageRate, "Mortgage rate", 0.25);
    const requestedTermYears = nonNegative(input.mortgageTermYears, "Mortgage term");
    if (requestedTermYears <= 0) throw new Error("Mortgage term must be positive");
    if (!new Set(["personal", "rental"]).has(input.useBeforeRetirement)) {
      throw new Error("Use before retirement must be personal or rental");
    }
    if (!new Set(["payoff", "continue"]).has(input.mortgageTreatment)) {
      throw new Error("Mortgage treatment must be payoff or continue");
    }

    const profile = input.mortgageProfile || {};
    const reasons = [];
    const mortgageRequested = requestedLtv > 0;
    let supported = !mortgageRequested ||
      !new Set(["no_standard_nonresident_route", "research_incomplete"]).has(profile.availability);
    if (!supported) reasons.push("No supported standard mortgage route is documented for this buyer profile.");
    const maximumLtv = profile.maximum_ltv === null || profile.maximum_ltv === undefined
      ? requestedLtv
      : rate(profile.maximum_ltv, "Destination maximum loan-to-value", 1);
    const effectiveLtv = supported ? Math.min(requestedLtv, maximumLtv) : 0;
    if (supported && effectiveLtv < requestedLtv) {
      reasons.push("Requested financing is limited to " + Math.round(effectiveLtv * 100) + "% for this destination.");
    }
    const profileTerm = profile.maximum_term_years === null || profile.maximum_term_years === undefined
      ? requestedTermYears
      : nonNegative(profile.maximum_term_years, "Destination maximum mortgage term");
    const mortgageTermYears = Math.min(requestedTermYears, profileTerm);
    if (mortgageTermYears < requestedTermYears) {
      reasons.push("Mortgage term is limited to " + mortgageTermYears + " years for this destination.");
    }
    if (mortgageRequested && profile.maximum_age_at_maturity !== null && profile.maximum_age_at_maturity !== undefined &&
        currentAge + mortgageTermYears > Number(profile.maximum_age_at_maturity)) {
      supported = false;
      reasons.push("Mortgage maturity exceeds the documented borrower age limit.");
    }

    const mortgagePrincipal = propertyPrice * effectiveLtv;
    const acquisitionCosts = propertyPrice * acquisitionCostRate;
    const cashRequiredToday = propertyPrice - mortgagePrincipal + acquisitionCosts;
    if (cashRequiredToday > maximumPropertyAllocation) {
      supported = false;
      reasons.push("Cash required exceeds your maximum property allocation.");
    }
    if (cashRequiredToday > totalLiquidCapital) {
      supported = false;
      reasons.push("Cash required exceeds total liquid capital.");
    }
    const startingPortfolio = totalLiquidCapital - cashRequiredToday;
    const mortgageTermMonths = Math.round(mortgageTermYears * 12);
    const payment = monthlyMortgagePayment({
      principal: mortgagePrincipal,
      annualRate: annualMortgageRate,
      termMonths: mortgageTermMonths,
    });
    const monthlyMortgageRate = annualMortgageRate / 12;
    const monthlyPortfolioReturn = Math.pow(1 + expectedPortfolioReturn, 1 / 12) - 1;
    const monthlyPropertyInflation = Math.pow(1 + propertyInflation, 1 / 12) - 1;
    let portfolio = startingPortfolio;
    let propertyValue = propertyPrice;
    let mortgageBalance = mortgagePrincipal;
    let exhaustedMonth = startingPortfolio < 0 ? 0 : null;
    const annualProjection = [{
      year: 0,
      portfolio: portfolio,
      propertyValue: propertyValue,
      mortgageBalance: mortgageBalance,
      grossRent: 0,
      netPropertyCashFlow: 0,
      netPortfolioContributions: 0,
    }];
    let yearGrossRent = 0;
    let yearPropertyCashFlow = 0;
    let yearPortfolioContributions = 0;

    for (let month = 0; month < monthsToRetirement; month += 1) {
      const completedYears = Math.floor(month / 12);
      const contribution = monthlyPortfolioContribution * (
        input.contributionInflationLinked ? Math.pow(1 + generalInflation, completedYears) : 1
      );
      const grossRent = input.useBeforeRetirement === "rental"
        ? propertyValue * grossRentalYield / 12
        : 0;
      const collectedRent = grossRent * (1 - vacancyRate);
      const rentalOperatingCosts = collectedRent * operatingCostRate;
      const ownerCosts = annualOwnerCosts * Math.pow(1 + ownerCostInflation, completedYears) / 12;
      let mortgagePayment = 0;
      if (mortgageBalance > 0 && month < mortgageTermMonths) {
        const interest = mortgageBalance * monthlyMortgageRate;
        const principalPart = Math.min(mortgageBalance, payment - interest);
        mortgageBalance = Math.max(0, mortgageBalance - principalPart);
        mortgagePayment = interest + principalPart;
      }
      const netPropertyCashFlow = collectedRent - rentalOperatingCosts - ownerCosts - mortgagePayment;
      const netContribution = contribution + netPropertyCashFlow;
      portfolio = portfolio * (1 + monthlyPortfolioReturn) + netContribution;
      propertyValue *= 1 + monthlyPropertyInflation;
      if (portfolio < 0 && exhaustedMonth === null) exhaustedMonth = month + 1;
      yearGrossRent += grossRent;
      yearPropertyCashFlow += netPropertyCashFlow;
      yearPortfolioContributions += netContribution;
      if ((month + 1) % 12 === 0) {
        annualProjection.push({
          year: (month + 1) / 12,
          portfolio: portfolio,
          propertyValue: propertyValue,
          mortgageBalance: mortgageBalance,
          grossRent: yearGrossRent,
          netPropertyCashFlow: yearPropertyCashFlow,
          netPortfolioContributions: yearPortfolioContributions,
        });
        yearGrossRent = 0;
        yearPropertyCashFlow = 0;
        yearPortfolioContributions = 0;
      }
    }

    const mortgageBalanceBeforeTreatment = mortgageBalance;
    let remainingMortgagePayments = Math.max(0, mortgageTermMonths - monthsToRetirement);
    if (input.mortgageTreatment === "payoff") {
      portfolio -= mortgageBalanceBeforeTreatment;
      mortgageBalance = 0;
      remainingMortgagePayments = 0;
      if (portfolio < 0 && exhaustedMonth === null) exhaustedMonth = monthsToRetirement;
    }
    if (exhaustedMonth !== null) {
      supported = false;
      reasons.push("The liquid portfolio is exhausted before or at retirement.");
    }

    return {
      supported: supported,
      reasons: reasons,
      effectiveLtv: effectiveLtv,
      mortgagePrincipal: mortgagePrincipal,
      monthlyMortgagePayment: payment,
      acquisitionCosts: acquisitionCosts,
      cashRequiredToday: cashRequiredToday,
      startingPortfolio: startingPortfolio,
      annualProjection: annualProjection,
      portfolioAtRetirement: portfolio,
      propertyValueAtRetirement: propertyValue,
      mortgageBalanceBeforeTreatment: mortgageBalanceBeforeTreatment,
      mortgageBalanceAtRetirement: mortgageBalance,
      propertyEquityAtRetirement: propertyValue - mortgageBalance,
      netRentalCashFlowAtRetirement: annualProjection[annualProjection.length - 1].netPropertyCashFlow,
      remainingMortgagePayments: remainingMortgagePayments,
      exhaustedMonth: exhaustedMonth,
    };
  }

  return {
    monthlyMortgagePayment: monthlyMortgagePayment,
    amortizeMortgage: amortizeMortgage,
    evaluateBuyNow: evaluateBuyNow,
  };
});
