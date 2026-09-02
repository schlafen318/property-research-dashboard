(function (root, factory) {
  const retirement = typeof module === "object" && module.exports
    ? require("./retirement_calculator.js")
    : root.GHARetirementCalculator;
  const propertyFinance = typeof module === "object" && module.exports
    ? require("./property_finance.js")
    : root.GHAPropertyFinance;
  const taxScenarios = typeof module === "object" && module.exports
    ? require("./fire_tax_scenarios.js")
    : root.GHAFireTaxScenarios;
  const calculatorUI = typeof module === "object" && module.exports
    ? require("./retirement_calculator_ui.js")
    : root.GHARetirementCalculatorUI;
  const api = factory(retirement, propertyFinance, taxScenarios, calculatorUI);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementDestinationFinder = api;
})(typeof window !== "undefined" ? window : null, function (retirement, propertyFinance, taxScenarios, calculatorUI) {
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
      retirementBeginsNow: user.retirementBeginsNow === true,
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

  function normalizedPreference(value) {
    return String(value || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "");
  }

  function normalizedSettings(preferences) {
    const source = Array.isArray(preferences.settings)
      ? preferences.settings
      : [preferences.climate];
    const normalized = source.map(normalizedPreference).filter(function (value, index, values) {
      return value && value !== "any" && values.indexOf(value) === index;
    });
    return normalized.reduce(function (settings, value) {
      const expanded = value === "water" || value === "coastorisland"
        ? ["coast", "island"]
        : [value];
      expanded.forEach(function (setting) {
        if (settings.indexOf(setting) === -1) settings.push(setting);
      });
      return settings;
    }, []);
  }

  function destinationSettings(destination) {
    if (Array.isArray(destination.settings) && destination.settings.length) {
      return destination.settings.map(normalizedPreference).filter(Boolean);
    }
    const category = normalizedPreference(destination.category);
    return {
      city: ["city"],
      coast: ["coast"],
      island: ["island"],
      lake: ["lake"],
      mountain: ["mountain"],
      water: ["coast", "island"],
      mountainwater: ["mountain", "coast", "island", "lake"],
    }[category] || [];
  }

  function destinationMatchesFilters(destination, preferences) {
    const region = normalizedPreference(preferences.region);
    const settings = normalizedSettings(preferences);
    const regionMatches = !region || region === "any" ||
      [destination.continent, destination.country].some(function (value) {
        return normalizedPreference(value) === region;
      });
    const availableSettings = destinationSettings(destination);
    const settingMatches = !settings.length || settings.some(function (setting) {
      return availableSettings.indexOf(setting) !== -1;
    });
    return regionMatches && settingMatches;
  }

  function preferenceMatches(destination, preferences) {
    const matches = [];
    if (preferences.region && preferences.region !== "any" &&
        destinationMatchesFilters(destination, { region: preferences.region, climate: "any" })) {
      matches.push("Preferred region");
    }
    if (normalizedSettings(preferences).length &&
        destinationMatchesFilters(destination, { region: "any", settings: preferences.settings, climate: preferences.climate })) {
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
    return { within_reach: 0, close: 1, stretch: 2, conditional: 3 }[tier];
  }

  function unavailableTaxScenario(reason) {
    return {
      status: "unavailable",
      conditional: true,
      explanations: [{ reason: reason }],
    };
  }

  function destinationTaxScenario(input, destination, cost) {
    const user = input.user || {};
    const profile = user.taxProfile || {};
    const planning = input.taxPlanning || {};
    const country = planning.countries && planning.countries[destination.country];
    try {
      return taxScenarios.estimateTaxScenario({
        taxMode: user.taxMode || "user_after_tax",
        stayMode: profile.stayMode || "full_relocation",
        dependableIncome: profile.dependableIncome || 0,
        portfolioWithdrawals: profile.portfolioWithdrawals || 0,
        realizedGainIntensity: profile.realizedGainIntensity,
        propertyUse: profile.propertyUse,
        wealthBand: profile.wealthBand,
        propertyTaxIncludedInRetirementCosts: user.housingPlan !== "rent",
        propertyPrice: Number(cost.property.representative_price_usd),
        asOf: planning.asOf,
      }, country);
    } catch (error) {
      return unavailableTaxScenario(error && error.message ? error.message : "Tax scenario inputs are invalid.");
    }
  }

  function targetCases(baseInput, taxScenario) {
    if (taxScenario.status === "unavailable") return null;
    const results = calculatorUI.calculateTaxAdjustedScenarios(baseInput, taxScenario);
    if (taxScenario.status === "user_after_tax") {
      const row = results.user_after_tax;
      return {
        central: Number(row.result.totalCapitalAtRetirement),
        annualTaxReserve: Number(row.annualTaxReserve),
        returnBasis: row.result.returnBasis,
      };
    }
    return {
      favorable: Number(results.favorable.result.totalCapitalAtRetirement),
      central: Number(results.central.result.totalCapitalAtRetirement),
      adverse: Number(results.adverse.result.totalCapitalAtRetirement),
      annualTaxReserve: Number(results.central.annualTaxReserve),
      returnBasis: results.central.result.returnBasis,
    };
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
    let evaluatedCount = 0;

    input.destinations.forEach(function (destination) {
      if (!destinationMatchesFilters(destination, user.preferences || {})) return;
      evaluatedCount += 1;
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
      const baseTargetInput = retirementTargetInput(user, cost);
      const taxScenario = destinationTaxScenario(input, destination, cost);
      const targets = targetCases(baseTargetInput, taxScenario);
      let retirementTarget = targets ? targets.central : null;
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
        const mortgageLiability = mortgageLiabilityAtRetirement(propertyResult, Number(user.expectedPortfolioReturn));
        if (targets) {
          targets.central += mortgageLiability;
          if (Number.isFinite(targets.favorable)) targets.favorable += mortgageLiability;
          if (Number.isFinite(targets.adverse)) targets.adverse += mortgageLiability;
          retirementTarget = targets.central;
        }
        financingReason = propertyResult.reasons[0] || (mortgageProfile.conditions || [])[0] || "";
      }

      const fundingRatio = retirementTarget === null
        ? null
        : (retirementTarget > 0 ? portfolioAtRetirement / retirementTarget : Infinity);
      const tier = fundingRatio === null ? "conditional" : fundingTier(fundingRatio);
      const matches = preferenceMatches(destination, user.preferences || {});
      const recommendation = {
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
        surplusGap: retirementTarget === null ? null : portfolioAtRetirement - retirementTarget,
        taxStatus: taxScenario.status,
        taxReason: taxScenario.explanations && taxScenario.explanations[0]
          ? taxScenario.explanations[0].reason
          : "",
        conditional: taxScenario.status === "unavailable" || taxScenario.conditional === true,
        annualTaxReserve: targets ? targets.annualTaxReserve : null,
        returnBasis: targets ? targets.returnBasis : null,
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
      };
      if (taxScenario.status !== "user_after_tax") {
        recommendation.retirementTargetRange = targets
          ? [targets.favorable, targets.adverse]
          : [null, null];
        recommendation.favorableGap = targets ? portfolioAtRetirement - targets.favorable : null;
        recommendation.adverseGap = targets ? portfolioAtRetirement - targets.adverse : null;
      }
      recommendations.push(recommendation);
    });

    recommendations.sort(function (left, right) {
      return tierOrder(left.tier) - tierOrder(right.tier) ||
        right.preferenceMatches.length - left.preferenceMatches.length ||
        right.fundingRatio - left.fundingRatio ||
        left.name.localeCompare(right.name);
    });
    return {
      summary: {
        evaluatedCount: evaluatedCount,
        withinReachCount: recommendations.filter(function (item) { return item.tier === "within_reach"; }).length,
        closeCount: recommendations.filter(function (item) { return item.tier === "close"; }).length,
        stretchCount: recommendations.filter(function (item) { return item.tier === "stretch"; }).length,
        conditionalCount: recommendations.filter(function (item) { return item.tier === "conditional"; }).length,
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
