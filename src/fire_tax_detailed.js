(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxDetailed = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  const CONFIDENCE = ["low", "medium", "medium_high", "high"];

  class DetailedFireTaxInputError extends Error {
    constructor(message) {
      super(message);
      this.name = "DetailedFireTaxInputError";
    }
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function dependency(globalName, path) {
    if (root && root[globalName]) return root[globalName];
    if (typeof require === "function") return require(path);
    throw new Error(globalName + " is required");
  }

  function residenceApi() { return dependency("GHAFireTaxResidence", "./fire_tax_residence.js"); }
  function incomeApi() { return dependency("GHAFireTaxIncome", "./fire_tax_income.js"); }
  function creditsApi() { return dependency("GHAFireTaxCredits", "./fire_tax_credits.js"); }
  function propertyApi() { return dependency("GHAFireTaxProperty", "./fire_tax_property.js"); }
  function retirementUiApi() { return dependency("GHARetirementCalculatorUI", "./retirement_calculator_ui.js"); }

  function unique(values) {
    const seen = new Set();
    return (values || []).filter(function (value) {
      if (typeof value !== "string" || !value || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }

  function round(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
  }

  function finiteAmount(value) {
    return typeof value === "number" && Number.isFinite(value) && value >= 0;
  }

  function amountRange(value, label) {
    if (finiteAmount(value)) return { minimum: value, maximum: value };
    if (record(value) && finiteAmount(value.minimum) && finiteAmount(value.maximum) && value.minimum <= value.maximum) {
      return { minimum: value.minimum, maximum: value.maximum };
    }
    throw new DetailedFireTaxInputError(label + " must be a non-negative amount or calculated range");
  }

  function normalizedAmount(range) {
    const minimum = round(range.minimum);
    const maximum = round(range.maximum);
    return minimum === maximum ? minimum : { minimum: minimum, maximum: maximum };
  }

  function addAmounts(values, label) {
    const total = values.reduce(function (sum, value, index) {
      const range = amountRange(value, label + "[" + index + "]");
      return { minimum: sum.minimum + range.minimum, maximum: sum.maximum + range.maximum };
    }, { minimum: 0, maximum: 0 });
    return normalizedAmount(total);
  }

  function subtractAmounts(left, right, label) {
    const minuend = amountRange(left, label + " minuend");
    const subtrahend = amountRange(right, label + " subtrahend");
    return normalizedAmount({
      minimum: Math.max(0, minuend.minimum - subtrahend.maximum),
      maximum: Math.max(0, minuend.maximum - subtrahend.minimum)
    });
  }

  function confidenceOf(values) {
    return values.reduce(function (lowest, value) {
      return CONFIDENCE.indexOf(value) < CONFIDENCE.indexOf(lowest) ? value : lowest;
    }, "high");
  }

  function validateHeader(profile, rules) {
    if (!record(profile) || !record(rules)) throw new DetailedFireTaxInputError("profile and rules are required objects");
    if (!record(profile.residence) || !record(profile.destination) || !record(profile.retirement)) {
      throw new DetailedFireTaxInputError("profile must include residence, destination, and retirement sections");
    }
    if (!record(rules.residence) || !record(rules.residence.destination) || !record(rules.residence.home) || !record(rules.destination)) {
      throw new DetailedFireTaxInputError("rules must include validated residence and destination bundles");
    }
    if (!record(rules.destination.income) || !Array.isArray(rules.destination.credits) || !record(rules.destination.property)) {
      throw new DetailedFireTaxInputError("destination rules must include income, credits, and property bundles");
    }
    if (!record(profile.destination.income) || !record(profile.destination.property)) {
      throw new DetailedFireTaxInputError("destination profile must include income and property facts");
    }
    const home = profile.continuingHome || { enabled: false };
    if (home.enabled !== true && home.enabled !== false) throw new DetailedFireTaxInputError("continuingHome.enabled must be boolean");
    if (home.enabled && (!record(home.income) || !record(home.property) || !record(rules.continuingHome) ||
        !record(rules.continuingHome.income) || !Array.isArray(rules.continuingHome.credits) || !record(rules.continuingHome.property))) {
      throw new DetailedFireTaxInputError("enabled continuing-home overlay requires validated income, credit, and property bundles");
    }
  }

  function calculateJurisdiction(profile, residence, rules) {
    const incomeCategories = incomeApi().calculateIncomeTax(profile.income, residence, rules.income);
    const credits = creditsApi().applyForeignTaxCredits(incomeCategories, rules.credits);
    const property = propertyApi().calculatePropertyTaxes(profile.property, residence, rules.property);
    return { incomeCategories: incomeCategories, credits: credits, property: property };
  }

  function disabledHome() {
    return { enabled: false, incomeCategories: [], credits: null, property: null };
  }

  function categoryMap(jurisdiction) {
    return Object.fromEntries((jurisdiction.credits ? jurisdiction.credits.categories : []).map(function (category) {
      return [category.category, category];
    }));
  }

  function validateTreatments(retirement, categories) {
    const fields = ["dependableIncomeCategories", "returnCoveredCategories", "annualExpenseCategories"];
    const membership = {};
    fields.forEach(function (field) {
      if (!Array.isArray(retirement[field]) || new Set(retirement[field]).size !== retirement[field].length) {
        throw new DetailedFireTaxInputError(field + " must be a distinct category list");
      }
      retirement[field].forEach(function (category) {
        membership[category] = (membership[category] || 0) + 1;
      });
    });
    categories.forEach(function (category) {
      if (membership[category] !== 1) {
        throw new DetailedFireTaxInputError("income category " + category + " must have exactly one retirement treatment");
      }
    });
    Object.keys(membership).forEach(function (category) {
      if (!categories.includes(category)) throw new DetailedFireTaxInputError("unknown retirement income category " + category);
    });
  }

  function categoryAmount(category, field) {
    if (!category || category.status === "out_of_scope" || category[field] === null || category[field] === undefined) return null;
    return category[field];
  }

  function sumCategoryField(jurisdictions, categoryNames, field) {
    const values = [];
    jurisdictions.forEach(function (jurisdiction) {
      const categories = categoryMap(jurisdiction);
      categoryNames.forEach(function (name) {
        const value = categoryAmount(categories[name], field);
        if (value !== null) values.push(value);
      });
    });
    return addAmounts(values, field);
  }

  function activeRentalTax(propertyResult) {
    if (!propertyResult || !record(propertyResult.stages) || !record(propertyResult.stages.rental)) return null;
    return propertyResult.stages.rental.taxTotal;
  }

  function uniquePropertyAnnualTax(propertyResult, treatment) {
    const annual = propertyResult.totals.annualTax;
    const rental = activeRentalTax(propertyResult);
    if (rental === null) return annual;
    if (!treatment) {
      throw new DetailedFireTaxInputError("propertyRentalTaxTreatment is required when property rental tax and rental income tax are both active");
    }
    if (!new Set(["included_in_income_tax", "separate_property_tax"]).has(treatment)) {
      throw new DetailedFireTaxInputError("propertyRentalTaxTreatment is invalid");
    }
    return treatment === "included_in_income_tax"
      ? subtractAmounts(annual, rental, "unique property annual tax")
      : annual;
  }

  function propertyAmounts(jurisdictions, treatment) {
    const active = jurisdictions.filter(function (jurisdiction) { return jurisdiction.property; });
    const uniqueAnnual = active.map(function (jurisdiction) {
      return uniquePropertyAnnualTax(jurisdiction.property, treatment);
    });
    const ownerCovered = active.map(function (jurisdiction) {
      return jurisdiction.property.retirementIntegration.ownerPropertyTaxAlreadyInLivingCosts;
    });
    const annualExpense = active.map(function (jurisdiction, index) {
      return subtractAmounts(uniqueAnnual[index], ownerCovered[index], "property annual retirement expense");
    });
    return {
      uniqueAnnual: addAmounts(uniqueAnnual, "property unique annual tax"),
      ownerCovered: addAmounts(ownerCovered, "owner property tax boundary"),
      annualExpense: addAmounts(annualExpense, "property annual tax expense"),
      oneTime: addAmounts(active.map(function (jurisdiction) { return jurisdiction.property.totals.oneTimeTax; }), "property one-time tax")
    };
  }

  function collectAudit(residence, destination, home) {
    const components = [residence, destination.credits, destination.property];
    if (home.enabled) components.push(home.credits, home.property);
    const ruleIds = unique(components.flatMap(function (component) { return component && component.ruleIds || component && component.creditRuleIds || []; })
      .concat(destination.credits.categories.flatMap(function (category) { return (category.ruleIds || []).concat(category.creditRuleIds || []); }))
      .concat(home.enabled ? home.credits.categories.flatMap(function (category) { return (category.ruleIds || []).concat(category.creditRuleIds || []); }) : []));
    const sourceIds = unique(components.flatMap(function (component) { return component && component.sourceIds || component && component.creditSourceIds || []; })
      .concat(destination.credits.categories.flatMap(function (category) { return (category.sourceIds || []).concat(category.creditSourceIds || []); }))
      .concat(home.enabled ? home.credits.categories.flatMap(function (category) { return (category.sourceIds || []).concat(category.creditSourceIds || []); }) : []));
    const confidences = [destination.credits.confidence, destination.property.confidence];
    if (home.enabled) confidences.push(home.credits.confidence, home.property.confidence);
    return { ruleIds: ruleIds, sourceIds: sourceIds, confidence: confidenceOf(confidences) };
  }

  function assertUnifiedUnits(residence, destination, home) {
    const components = [destination.credits, destination.property];
    if (home.enabled) components.push(home.credits, home.property);
    const currencies = unique(components.map(function (component) { return component.currency; }));
    if (currencies.length !== 1) {
      throw new DetailedFireTaxInputError("all detailed tax components must use one currency before totals are calculated");
    }
    const taxYears = new Set(components.map(function (component) { return component.taxYear; }).concat([residence.taxYear]));
    if (taxYears.size !== 1) {
      throw new DetailedFireTaxInputError("all detailed tax components must use one tax year before totals are calculated");
    }
  }

  function calculateDetailedTax(profile, rules) {
    validateHeader(profile, rules);
    const residence = residenceApi().evaluateResidence(profile.residence, rules.residence.destination, rules.residence.home);
    const destination = calculateJurisdiction(profile.destination, residence, rules.destination);
    const home = profile.continuingHome && profile.continuingHome.enabled
      ? Object.assign({ enabled: true }, calculateJurisdiction(profile.continuingHome, residence, rules.continuingHome))
      : disabledHome();
    assertUnifiedUnits(residence, destination, home);
    const jurisdictions = [destination].concat(home.enabled ? [home] : []);
    const destinationCategories = destination.credits.categories.map(function (category) { return category.category; });
    validateTreatments(profile.retirement, destinationCategories);
    if (profile.retirement.returnBasis !== "after_fees_and_tax") {
      throw new DetailedFireTaxInputError("selected return must use the explicit after_fees_and_tax basis");
    }
    if (typeof profile.retirement.selectedAfterTaxReturn !== "number" || !Number.isFinite(profile.retirement.selectedAfterTaxReturn)) {
      throw new DetailedFireTaxInputError("selectedAfterTaxReturn must be a finite explicit rate");
    }

    const dependableTax = sumCategoryField(jurisdictions, profile.retirement.dependableIncomeCategories, "netTax");
    const returnCoveredTax = sumCategoryField(jurisdictions, profile.retirement.returnCoveredCategories, "netTax");
    const incomeExpenseTax = sumCategoryField(jurisdictions, profile.retirement.annualExpenseCategories, "netTax");
    const grossDependableIncome = sumCategoryField([destination], profile.retirement.dependableIncomeCategories, "grossIncome");
    const afterTaxDependableIncome = subtractAmounts(grossDependableIncome, dependableTax, "after-tax dependable income");
    const property = propertyAmounts(jurisdictions, profile.retirement.propertyRentalTaxTreatment);
    const annualTaxExpense = addAmounts([incomeExpenseTax, property.annualExpense], "retirement annual tax expense");
    const annualTax = addAmounts([dependableTax, returnCoveredTax, incomeExpenseTax, property.uniqueAnnual], "reconciled annual tax");
    const audit = collectAudit(residence, destination, home);
    const retirementIntegration = {
      dependableIncomeTax: dependableTax,
      returnCoveredTax: returnCoveredTax,
      livingCostCoveredTax: property.ownerCovered,
      annualTaxExpense: annualTaxExpense,
      propertyRentalTaxTreatment: profile.retirement.propertyRentalTaxTreatment || null,
      exclusions: [
        "Dependable-income tax is netted from the dependable income stream.",
        "Tax on return-covered income is represented by the selected after-fees-and-tax return.",
        "Owner property tax already included in living costs is not added again.",
        "Property value and equity remain outside liquid retirement income."
      ]
    };
    const retirementProjection = retirementUiApi().calculateDetailedRetirement(profile.retirement.baseInput, {
      annualTaxExpenses: annualTaxExpense,
      afterTaxDependableIncome: afterTaxDependableIncome,
      selectedAfterTaxReturn: profile.retirement.selectedAfterTaxReturn,
      returnBasis: profile.retirement.returnBasis,
      dependableIncomeIndexed: profile.retirement.dependableIncomeIndexed,
      dependableIncomeInflationRate: profile.retirement.dependableIncomeInflationRate,
      planningRange: profile.retirement.planningRange
    });
    const taxAdjustedCapitalInput = retirementProjection.input;

    return {
      status: [residence.status, destination.property.status, home.enabled ? home.property.status : "calculated"].includes("conditional") ? "conditional" : "calculated",
      currency: destination.credits.currency,
      taxYear: destination.credits.taxYear,
      residence: residence,
      destination: destination,
      continuingHome: home,
      totals: {
        annualTax: annualTax,
        oneTimeTaxes: property.oneTime,
        grossDependableIncome: grossDependableIncome,
        afterTaxDependableIncome: afterTaxDependableIncome
      },
      afterTaxReturnBasis: {
        rate: profile.retirement.selectedAfterTaxReturn,
        basis: profile.retirement.returnBasis,
        formula: "User-selected portfolio return after fees and tax."
      },
      retirementIntegration: retirementIntegration,
      taxAdjustedCapitalInput: taxAdjustedCapitalInput,
      retirementProjection: retirementProjection,
      ruleIds: audit.ruleIds,
      sourceIds: audit.sourceIds,
      confidence: audit.confidence
    };
  }

  return {
    calculateDetailedTax: calculateDetailedTax,
    DetailedFireTaxInputError: DetailedFireTaxInputError
  };
});
