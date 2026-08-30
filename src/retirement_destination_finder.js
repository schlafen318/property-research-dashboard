(function (root, factory) {
  const retirement = typeof module === "object" && module.exports
    ? require("./retirement_calculator.js")
    : root.GHARetirementCalculator;
  const propertyFinance = typeof module === "object" && module.exports
    ? require("./property_finance.js")
    : root.GHAPropertyFinance;
  const api = factory(retirement, propertyFinance);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementDestinationFinder = api;
})(typeof window !== "undefined" ? window : null, function (retirement, propertyFinance) {
  "use strict";

  function number(value, label) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) throw new Error(label + " must be finite");
    return parsed;
  }

  function nonNegative(value, label) {
    const parsed = number(value, label);
    if (parsed < 0) throw new Error(label + " must be non-negative");
    return parsed;
  }

  function projectPortfolio(input) {
    const currentAge = nonNegative(input.currentAge, "Current age");
    const retirementAge = nonNegative(input.retirementAge, "Retirement age");
    const months = Math.round((retirementAge - currentAge) * 12);
    if (months <= 0) throw new Error("Retirement age must exceed current age");
    const startingPortfolio = nonNegative(input.startingPortfolio, "Starting portfolio");
    const monthlyContribution = nonNegative(input.monthlyContribution, "Monthly contribution");
    const generalInflation = nonNegative(input.generalInflation, "General inflation");
    const expectedReturn = number(input.expectedPortfolioReturn, "Expected portfolio return");
    if (generalInflation > 0.15) throw new Error("General inflation exceeds the allowed range");
    if (expectedReturn < -0.05 || expectedReturn > 0.15) {
      throw new Error("Expected portfolio return must be between -5% and 15%");
    }
    const monthlyReturn = Math.pow(1 + expectedReturn, 1 / 12) - 1;
    let portfolio = startingPortfolio;
    let exhaustedMonth = null;
    let annualContributions = 0;
    const annualProjection = [{ year: 0, portfolio: portfolio, contributions: 0 }];
    for (let month = 0; month < months; month += 1) {
      const completedYears = Math.floor(month / 12);
      const contribution = monthlyContribution * (
        input.contributionInflationLinked ? Math.pow(1 + generalInflation, completedYears) : 1
      );
      portfolio = portfolio * (1 + monthlyReturn) + contribution;
      annualContributions += contribution;
      if (portfolio < 0 && exhaustedMonth === null) exhaustedMonth = month + 1;
      if ((month + 1) % 12 === 0) {
        annualProjection.push({
          year: (month + 1) / 12,
          portfolio: portfolio,
          contributions: annualContributions,
        });
        annualContributions = 0;
      }
    }
    return {
      annualProjection: annualProjection,
      portfolioAtRetirement: portfolio,
      exhaustedMonth: exhaustedMonth,
    };
  }

  function categoryInflation(name, inflation) {
    return name === "private_healthcare" ? inflation.healthcare : inflation.general;
  }

  function retirementTargetInput(user, cost) {
    const profile = cost.profiles[user.household];
    if (!profile) throw new Error("Missing household retirement-cost profile");
    const categories = Object.keys(profile.categories_usd).map(function (name) {
      return {
        amount: Number(profile.categories_usd[name]),
        inflationRate: Number(categoryInflation(name, cost.inflation)),
      };
    });
    const housingAmount = user.housingPlan === "rent"
      ? profile.annual_rent_usd
      : profile.annual_owner_costs_usd;
    categories.push({ amount: Number(housingAmount), inflationRate: Number(cost.inflation.general) });
    return {
      currentAge: user.currentAge,
      retirementAge: user.retirementAge,
      horizonYears: user.horizonYears,
      expenseCategories: categories,
      incomeStreams: user.incomeStreams || [],
      housingPlan: user.housingPlan,
      propertyPrice: Number(cost.property.representative_price_usd),
      propertyInflation: Number(cost.inflation.property),
      acquisitionCostRate: Number(cost.property.acquisition_cost_rate),
      generalInflation: Number(user.generalInflation),
      emergencyReserveMonths: user.emergencyReserveMonths,
      expectedPortfolioReturn: user.expectedPortfolioReturn,
      monthlyIncomeBeforeRetirement: 0,
      incomeInvestedRate: 0,
    };
  }

  function scoreValue(destination, key) {
    const raw = destination.scores && destination.scores[key];
    return Number(raw && typeof raw === "object" ? raw.score : raw || 0);
  }

  function preferenceMatches(destination, preferences) {
    const matches = [];
    if (preferences.region && preferences.region !== "any" &&
        [destination.continent, destination.country].includes(preferences.region)) {
      matches.push("Preferred region");
    }
    if (preferences.climate && preferences.climate !== "any" &&
        String(destination.category || "").toLowerCase().includes(String(preferences.climate).toLowerCase())) {
      matches.push("Preferred setting");
    }
    if (preferences.healthcare === "high" && scoreValue(destination, "healthcare") >= 4) {
      matches.push("Stronger healthcare signal");
    }
    if (scoreValue(destination, "retirement_suitability") >= 4) {
      matches.push("Long-stay suitability");
    }
    return matches.slice(0, 2);
  }

  function fundingTier(ratio) {
    if (ratio + 1e-9 >= 1) return "within_reach";
    if (ratio + 1e-9 >= 0.85) return "close";
    return "stretch";
  }

  function tierOrder(tier) {
    return { within_reach: 0, close: 1, stretch: 2 }[tier];
  }

  function mortgageLiabilityAtRetirement(propertyResult, expectedReturn) {
    if (!propertyResult.remainingMortgagePayments) return 0;
    const payment = propertyResult.monthlyMortgagePayment;
    const monthlyReturn = Math.pow(1 + expectedReturn, 1 / 12) - 1;
    if (monthlyReturn === 0) return payment * propertyResult.remainingMortgagePayments;
    return payment * (1 - Math.pow(1 + monthlyReturn, -propertyResult.remainingMortgagePayments)) / monthlyReturn;
  }

  function financingLabel(profile, purchaseMethod) {
    if (purchaseMethod === "cash") return "Cash purchase";
    const label = {
      likely_available: "Likely available",
      conditional: "Available with conditions",
      no_standard_nonresident_route: "No standard non-resident route identified",
      research_incomplete: "Research incomplete",
    }[profile.availability] || "Research incomplete";
    return purchaseMethod === "not_sure" ? "Illustrative mortgage · " + label : label;
  }

  function projectionAfterRetirementTreatment(annualProjection, portfolioAtRetirement, mortgageBalanceAtRetirement) {
    if (!Array.isArray(annualProjection) || !annualProjection.length) return annualProjection;
    const adjusted = annualProjection.slice();
    adjusted[adjusted.length - 1] = Object.assign({}, adjusted[adjusted.length - 1], {
      portfolio: portfolioAtRetirement,
      mortgageBalance: mortgageBalanceAtRetirement,
    });
    return adjusted;
  }

  function profileMatchesBuyer(input) {
    const user = input && input.user || {};
    const profile = input && input.profile || {};
    const residencies = Array.isArray(profile.eligible_residency) ? profile.eligible_residency : [];
    const incomeSources = Array.isArray(profile.eligible_income_sources) ? profile.eligible_income_sources : [];
    const residency = user.residency || "non_resident";
    const incomeSource = user.incomeSource || "overseas";
    return residencies.includes(residency) && incomeSources.includes(incomeSource);
  }

  function recommendDestinations(input, projectionOverride) {
    if (!input || !Array.isArray(input.destinations) || !Array.isArray(input.retirementCosts)) {
      throw new Error("Destinations and retirement costs are required");
    }
    const user = input.user || {};
    const costs = new Map(input.retirementCosts.map(function (item) {
      return [item.destination_id, item];
    }));
    const sharedProjection = projectionOverride || (user.housingPlan === "buy_now" ? null : projectPortfolio({
        currentAge: user.currentAge,
        retirementAge: user.retirementAge,
        startingPortfolio: user.totalLiquidCapital,
        monthlyContribution: user.monthlyPortfolioContribution,
        contributionInflationLinked: user.contributionInflationLinked,
        generalInflation: user.generalInflation,
        expectedPortfolioReturn: user.expectedPortfolioReturn,
      }));
    const recommendations = [];
    const excluded = [];

    input.destinations.forEach(function (destination) {
      const cost = costs.get(destination.id);
      if (!cost) {
        excluded.push({ destinationId: destination.id, name: destination.name, reasonCode: "missing_cost_data" });
        return;
      }
      if (destination.recommendable === false) {
        excluded.push({ destinationId: destination.id, name: destination.name, reasonCode: "buyer_access_restricted" });
        return;
      }
      const retirementProfile = cost.profiles[user.household];
      const targetResult = retirement.calculateRetirementTarget(retirementTargetInput(user, cost));
      let retirementTarget = Number(targetResult.totalCapitalAtRetirement);
      let portfolioAtRetirement = sharedProjection ? sharedProjection.portfolioAtRetirement : 0;
      let annualProjection = sharedProjection ? sharedProjection.annualProjection : null;
      let propertyEquity = 0;
      let mortgageBalance = 0;
      let netRentalCashFlow = 0;
      let financingReason = "";
      const mortgageProfile = input.mortgageProfiles[destination.id] || {
        availability: "research_incomplete",
        maximum_ltv: null,
        conditions: [],
        confidence: "low",
      };

      if (user.housingPlan === "buy_now") {
        const mortgageRequested = user.purchaseMethod !== "cash" && Number(user.requestedLtv) > 0;
        if (mortgageRequested && mortgageProfile.availability === "research_incomplete") {
          excluded.push({ destinationId: destination.id, name: destination.name, reasonCode: "financing_unverified" });
          return;
        }
        if (mortgageRequested && mortgageProfile.availability === "no_standard_nonresident_route") {
          excluded.push({ destinationId: destination.id, name: destination.name, reasonCode: "no_standard_mortgage" });
          return;
        }
        if (mortgageRequested && !profileMatchesBuyer({ user: user, profile: mortgageProfile })) {
          excluded.push({ destinationId: destination.id, name: destination.name, reasonCode: "mortgage_profile_mismatch" });
          return;
        }
        const profile = cost.profiles[user.household];
        const propertyResult = propertyFinance.evaluateBuyNow({
          currentAge: user.currentAge,
          retirementAge: user.retirementAge,
          totalLiquidCapital: user.totalLiquidCapital,
          maximumPropertyAllocation: user.maximumPropertyAllocation,
          monthlyPortfolioContribution: user.monthlyPortfolioContribution,
          contributionInflationLinked: user.contributionInflationLinked,
          generalInflation: user.generalInflation,
          expectedPortfolioReturn: user.expectedPortfolioReturn,
          propertyPrice: cost.property.representative_price_usd,
          acquisitionCostRate: cost.property.acquisition_cost_rate,
          propertyInflation: cost.inflation.property,
          annualOwnerCosts: profile.annual_owner_costs_usd,
          ownerCostInflation: cost.inflation.general,
          useBeforeRetirement: user.useBeforeRetirement,
          grossRentalYield: user.grossRentalYield,
          vacancyRate: user.vacancyRate,
          operatingCostRate: user.operatingCostRate,
          requestedLtv: user.purchaseMethod === "cash" ? 0 : user.requestedLtv,
          annualMortgageRate: user.annualMortgageRate,
          mortgageTermYears: user.mortgageTermYears,
          mortgageTreatment: user.mortgageTreatment,
          mortgageProfile: mortgageProfile,
        });
        if (!propertyResult.supported) {
          excluded.push({
            destinationId: destination.id,
            name: destination.name,
            reasonCode: "property_finance_unavailable",
            reasons: propertyResult.reasons,
          });
          return;
        }
        portfolioAtRetirement = propertyResult.portfolioAtRetirement;
        annualProjection = projectionAfterRetirementTreatment(
          propertyResult.annualProjection,
          propertyResult.portfolioAtRetirement,
          propertyResult.mortgageBalanceAtRetirement
        );
        propertyEquity = propertyResult.propertyEquityAtRetirement;
        mortgageBalance = propertyResult.mortgageBalanceAtRetirement;
        netRentalCashFlow = propertyResult.netRentalCashFlowAtRetirement;
        retirementTarget += mortgageLiabilityAtRetirement(propertyResult, Number(user.expectedPortfolioReturn));
        financingReason = propertyResult.reasons[0] || (mortgageProfile.conditions || [])[0] || "";
      }

      const fundingRatio = retirementTarget > 0 ? portfolioAtRetirement / retirementTarget : Infinity;
      const tier = fundingTier(fundingRatio);
      const matches = preferenceMatches(destination, user.preferences || {});
      recommendations.push({
        destinationId: destination.id,
        name: destination.name,
        country: destination.country,
        tier: tier,
        fundingRatio: fundingRatio,
        portfolioAtRetirement: portfolioAtRetirement,
        annualProjection: annualProjection,
        retirementTarget: retirementTarget,
        monthlyRetirementCost: (
          Object.keys(retirementProfile.categories_usd).reduce(function (total, key) {
            return total + Number(retirementProfile.categories_usd[key] || 0);
          }, 0) + Number(user.housingPlan === "rent"
            ? retirementProfile.annual_rent_usd
            : retirementProfile.annual_owner_costs_usd)
        ) / 12,
        countryGuideHref: destination.countryGuideHref || "",
        surplusGap: portfolioAtRetirement - retirementTarget,
        propertyEquity: propertyEquity,
        mortgageBalance: mortgageBalance,
        netRentalCashFlow: netRentalCashFlow,
        financingStatus: financingLabel(mortgageProfile, user.purchaseMethod),
        financingReason: financingReason,
        preferenceMatches: matches,
        detailHref: "/retirement-abroad-calculator/?destination=" + encodeURIComponent(destination.id) +
          "&household=" + encodeURIComponent(user.household) +
          "&housing=" + encodeURIComponent(user.housingPlan),
        evidenceConfidence: mortgageProfile.confidence || "low",
      });
    });

    recommendations.sort(function (left, right) {
      return tierOrder(left.tier) - tierOrder(right.tier) ||
        right.preferenceMatches.length - left.preferenceMatches.length ||
        right.fundingRatio - left.fundingRatio ||
        left.name.localeCompare(right.name);
    });
    return {
      summary: {
        evaluatedCount: input.destinations.length,
        withinReachCount: recommendations.filter(function (item) { return item.tier === "within_reach"; }).length,
        closeCount: recommendations.filter(function (item) { return item.tier === "close"; }).length,
        stretchCount: recommendations.filter(function (item) { return item.tier === "stretch"; }).length,
      },
      sharedProjection: sharedProjection,
      recommendations: recommendations,
      excluded: excluded,
    };
  }

  function recommendProjectedCapital(input) {
    const user = input && input.user || {};
    if (user.housingPlan === "buy_now") {
      throw new Error("Projected-capital scenarios do not support buy now");
    }
    const capital = nonNegative(input && input.projectedCapitalUsd, "Projected capital");
    const sharedProjection = {
      annualProjection: [{
        year: Math.max(0, Number(user.retirementAge) - Number(user.currentAge)),
        portfolio: capital,
        contributions: 0,
      }],
      portfolioAtRetirement: capital,
      exhaustedMonth: null,
    };
    return recommendDestinations(input, sharedProjection);
  }

  return {
    projectPortfolio: projectPortfolio,
    retirementTargetInput: retirementTargetInput,
    fundingTier: fundingTier,
    profileMatchesBuyer: profileMatchesBuyer,
    recommendDestinations: recommendDestinations,
    recommendProjectedCapital: recommendProjectedCapital,
  };
});
