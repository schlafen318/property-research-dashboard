(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxDetailed = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  "use strict";

  const CONFIDENCE = ["low", "medium", "medium_high", "high"];
  const AMOUNT_FIELDS = ["grossIncome", "deductions", "taxableBase", "domesticTax", "sourceWithholding", "creditApplied", "netTax"];

  class DetailedFireTaxInputError extends Error {
    constructor(message) {
      super(message);
      this.name = "DetailedFireTaxInputError";
    }
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function containsConditional(value, seen) {
    if (value === null || typeof value !== "object") return false;
    const visited = seen || new Set();
    if (visited.has(value)) return false;
    visited.add(value);
    if (record(value) && value.status === "conditional") return true;
    return Object.keys(value).some(function (key) { return containsConditional(value[key], visited); });
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

  function rangeOf(values, label) {
    if (!Array.isArray(values) || values.length === 0) throw new DetailedFireTaxInputError(label + " has no calculated branch values");
    const endpoints = values.flatMap(function (value, index) {
      const range = amountRange(value, label + "[" + index + "]");
      return [range.minimum, range.maximum];
    });
    return normalizedAmount({ minimum: Math.min.apply(Math, endpoints), maximum: Math.max.apply(Math, endpoints) });
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
    if (profile.retirement.returnBasis !== "after_fees_and_tax") {
      throw new DetailedFireTaxInputError("selected return must use the explicit after_fees_and_tax basis");
    }
    if (typeof profile.retirement.selectedAfterTaxReturn !== "number" || !Number.isFinite(profile.retirement.selectedAfterTaxReturn)) {
      throw new DetailedFireTaxInputError("selectedAfterTaxReturn must be a finite explicit rate");
    }
  }

  function concreteResidence(node, period) {
    return Object.assign({}, node, {
      status: period ? period.status : node.status,
      scopes: period ? period.scopes : node.scopes,
      periods: period ? [period] : (node.periods || []).slice(),
      branches: []
    });
  }

  function residenceLeaves(result) {
    const leaves = [];
    function expand(node, path, inherited) {
      const identity = Object.assign({}, inherited, {
        residencePath: path.join("."),
        residenceStatus: node.status,
        scopes: node.scopes
      });
      if (Object.prototype.hasOwnProperty.call(node, "assumedValue")) identity.assumedValue = node.assumedValue;
      if (node.status === "conditional") {
        if (!Array.isArray(node.branches) || node.branches.length === 0) {
          throw new DetailedFireTaxInputError("residence branch " + identity.residencePath + " remains conditional and cannot be assigned a tax scope");
        }
        node.branches.forEach(function (branch, index) { expand(branch, path.concat(["branch" + index]), identity); });
        return;
      }
      const periods = Array.isArray(node.periods) ? node.periods.filter(function (period) {
        return record(period) && record(period.scopes) && period.status;
      }) : [];
      const distinctPeriods = periods.filter(function (period, index) {
        return index === periods.findIndex(function (candidate) {
          return candidate.status === period.status && JSON.stringify(candidate.scopes) === JSON.stringify(period.scopes);
        });
      });
      if (distinctPeriods.length > 1) {
        distinctPeriods.forEach(function (period, index) {
          const periodIdentity = Object.assign({}, identity, {
            residencePath: path.concat(["period" + index]).join("."),
            residenceStatus: period.status,
            scopes: period.scopes,
            period: { start: period.start, end: period.end }
          });
          leaves.push({ residence: concreteResidence(Object.assign({ taxYear: result.taxYear }, node), period), identity: periodIdentity });
        });
        return;
      }
      leaves.push({ residence: concreteResidence(Object.assign({ taxYear: result.taxYear }, node), null), identity: identity });
    }
    expand(result, ["residence"], {});
    return leaves;
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

  function propertyLeaves(result) {
    if (result.status === "conditional") {
      if (!Array.isArray(result.branches) || result.branches.length === 0) {
        throw new DetailedFireTaxInputError("conditional property result requires calculated branches");
      }
      return result.branches;
    }
    return [result];
  }

  function compatibleFacts(left, right) {
    const shared = Object.keys(left || {}).filter(function (key) { return Object.prototype.hasOwnProperty.call(right || {}, key); });
    return shared.every(function (key) { return left[key] === right[key]; });
  }

  function treatmentMap(retirement, categories) {
    const fields = {
      dependableIncomeCategories: "dependable_income",
      returnCoveredCategories: "return_covered",
      annualExpenseCategories: "annual_expense"
    };
    const membership = {};
    Object.keys(fields).forEach(function (field) {
      if (!Array.isArray(retirement[field]) || new Set(retirement[field]).size !== retirement[field].length) {
        throw new DetailedFireTaxInputError(field + " must be a distinct category list");
      }
      retirement[field].forEach(function (category) {
        membership[category] = membership[category] || [];
        membership[category].push(fields[field]);
      });
    });
    categories.forEach(function (category) {
      if (!membership[category] || membership[category].length !== 1) {
        throw new DetailedFireTaxInputError("income category " + category + " must have exactly one retirement treatment");
      }
    });
    Object.keys(membership).forEach(function (category) {
      if (!categories.includes(category)) throw new DetailedFireTaxInputError("unknown retirement income category " + category);
      if (membership[category].length !== 1) throw new DetailedFireTaxInputError("income category " + category + " must have exactly one retirement treatment");
    });
    return Object.fromEntries(Object.keys(membership).map(function (category) { return [category, membership[category][0]]; }));
  }

  function normalizedCanonicalIncome(destination, home, profile) {
    const observations = [];
    function add(side, jurisdiction, incomeProfile) {
      if (!jurisdiction || !jurisdiction.credits) return;
      const coveredCategories = jurisdiction.credits.categories.map(function (category) { return category.category; });
      const declaredCategories = Object.keys(incomeProfile.incomeSourceJurisdictions || {});
      const uncovered = declaredCategories.filter(function (category) { return !coveredCategories.includes(category); });
      if (uncovered.length) {
        throw new DetailedFireTaxInputError(side + " profile income category " + uncovered[0] + " has no validated rule coverage");
      }
      jurisdiction.credits.categories.forEach(function (category) {
        observations.push({
          side: side,
          category: category.category,
          grossAmount: category.grossIncome,
          currency: category.currency,
          taxYear: category.taxYear,
          sourceJurisdiction: incomeProfile.incomeSourceJurisdictions[category.category]
        });
      });
    }
    add("destination", destination, profile.destination.income);
    if (home.enabled) add("continuing_home", home, profile.continuingHome.income);
    const categoryNames = unique(observations.map(function (item) { return item.category; }));
    const treatments = treatmentMap(profile.retirement, categoryNames);
    const categories = categoryNames.map(function (category) {
      const matches = observations.filter(function (item) { return item.category === category; });
      const amounts = new Set(matches.map(function (item) { return item.grossAmount; }));
      const currencies = new Set(matches.map(function (item) { return item.currency; }));
      const years = new Set(matches.map(function (item) { return item.taxYear; }));
      const sources = new Set(matches.map(function (item) { return item.sourceJurisdiction; }));
      if (amounts.size !== 1 || currencies.size !== 1 || years.size !== 1 || sources.size !== 1) {
        throw new DetailedFireTaxInputError("income category " + category + " has inconsistent canonical profile amount, currency, tax year, or source jurisdiction");
      }
      const grossAmount = matches[0].grossAmount;
      if (!finiteAmount(grossAmount)) throw new DetailedFireTaxInputError("income category " + category + " lacks a canonical gross amount");
      return {
        category: category,
        grossAmount: grossAmount,
        currency: matches[0].currency,
        taxYear: matches[0].taxYear,
        sourceJurisdiction: matches[0].sourceJurisdiction,
        treatment: treatments[category],
        observedIn: matches.map(function (item) { return item.side; })
      };
    });
    return { categories: categories, currency: categories[0].currency, taxYear: categories[0].taxYear };
  }

  function categoryByName(jurisdiction) {
    return Object.fromEntries((jurisdiction.credits ? jurisdiction.credits.categories : []).map(function (category) {
      return [category.category, category];
    }));
  }

  function reconcileIncome(destination, home, canonical) {
    const jurisdictionEntries = [{ side: "destination", result: destination }];
    if (home.enabled) jurisdictionEntries.push({ side: "continuing_home", result: home });
    const withholdings = [];
    const liabilities = [];
    const credits = [];
    const categories = canonical.categories.map(function (canonicalCategory) {
      const categoryObservations = [];
      jurisdictionEntries.forEach(function (entry) {
        const category = categoryByName(entry.result)[canonicalCategory.category];
        if (!category || category.status === "out_of_scope") return;
        if (category.status !== "calculated") throw new DetailedFireTaxInputError("aligned income scenario contains a non-calculated category " + canonicalCategory.category);
        categoryObservations.push({ side: entry.side, category: category });
      });
      const categoryLiabilities = categoryObservations.map(function (observation) {
        const item = {
          identity: observation.side + "|" + canonicalCategory.category + "|" + canonicalCategory.taxYear,
          jurisdiction: observation.side,
          category: canonicalCategory.category,
          amount: observation.category.domesticTax,
          ruleIds: observation.category.ruleIds,
          sourceIds: observation.category.sourceIds
        };
        liabilities.push(item);
        return item;
      });
      const positiveWithholding = categoryObservations.filter(function (observation) { return observation.category.sourceWithholding > 0; });
      let uniqueWithholding = 0;
      let withholdingIdentity = null;
      if (positiveWithholding.length) {
        withholdingIdentity = [canonicalCategory.category, canonicalCategory.sourceJurisdiction, canonicalCategory.taxYear].join("|");
        const amounts = new Set(positiveWithholding.map(function (observation) { return observation.category.sourceWithholding; }));
        if (amounts.size !== 1) throw new DetailedFireTaxInputError("shared withholding identity " + withholdingIdentity + " has inconsistent amounts");
        uniqueWithholding = positiveWithholding[0].category.sourceWithholding;
        withholdings.push({
          identity: withholdingIdentity,
          category: canonicalCategory.category,
          sourceJurisdiction: canonicalCategory.sourceJurisdiction,
          amount: uniqueWithholding,
          countedAmount: uniqueWithholding,
          observedBy: positiveWithholding.map(function (observation) { return observation.side; }),
          countedOnce: true,
          ruleIds: unique(positiveWithholding.flatMap(function (observation) { return observation.category.ruleIds; })),
          sourceIds: unique(positiveWithholding.flatMap(function (observation) { return observation.category.sourceIds; }))
        });
      }
      const categoryCreditClaims = categoryObservations.filter(function (observation) { return observation.category.creditApplied > 0; }).map(function (observation) {
        return {
          jurisdiction: observation.side,
          category: canonicalCategory.category,
          withholdingIdentity: withholdingIdentity,
          claimedAmount: observation.category.creditApplied,
          ruleIds: observation.category.creditRuleIds,
          sourceIds: observation.category.creditSourceIds
        };
      });
      const domesticLiability = round(categoryLiabilities.reduce(function (sum, item) { return sum + item.amount; }, 0));
      const creditClaimed = round(categoryCreditClaims.reduce(function (sum, item) { return sum + item.claimedAmount; }, 0));
      const creditApplied = round(Math.min(creditClaimed, uniqueWithholding, domesticLiability));
      let remainingCredit = creditApplied;
      categoryCreditClaims.forEach(function (claim) {
        const applied = round(Math.min(claim.claimedAmount, remainingCredit));
        remainingCredit = round(remainingCredit - applied);
        credits.push(Object.assign({}, claim, { appliedAmount: applied }));
      });
      const netTax = round(domesticLiability + uniqueWithholding - creditApplied);
      return {
        category: canonicalCategory.category,
        treatment: canonicalCategory.treatment,
        grossAmount: canonicalCategory.grossAmount,
        domesticLiability: domesticLiability,
        uniqueWithholding: uniqueWithholding,
        creditClaimed: creditClaimed,
        creditApplied: creditApplied,
        netTax: netTax,
        withholdingIdentity: withholdingIdentity,
        liabilityIds: categoryLiabilities.map(function (item) { return item.identity; })
      };
    });
    return {
      status: "calculated",
      categories: categories,
      liabilities: liabilities,
      withholdings: withholdings,
      credits: credits,
      totalDomesticLiability: round(categories.reduce(function (sum, item) { return sum + item.domesticLiability; }, 0)),
      totalUniqueWithholding: round(categories.reduce(function (sum, item) { return sum + item.uniqueWithholding; }, 0)),
      totalCreditClaimed: round(categories.reduce(function (sum, item) { return sum + item.creditClaimed; }, 0)),
      totalCreditApplied: round(categories.reduce(function (sum, item) { return sum + item.creditApplied; }, 0)),
      totalNetIncomeTax: round(categories.reduce(function (sum, item) { return sum + item.netTax; }, 0))
    };
  }

  function activeRentalTax(propertyResult) {
    if (!propertyResult || !record(propertyResult.stages) || !record(propertyResult.stages.rental)) return null;
    return propertyResult.stages.rental.taxTotal;
  }

  function uniquePropertyAnnualTax(propertyResult, treatment) {
    const annual = propertyResult.totals.annualTax;
    const rental = activeRentalTax(propertyResult);
    if (rental === null) return annual;
    if (!treatment) throw new DetailedFireTaxInputError("propertyRentalTaxTreatment is required when property rental tax and rental income tax are both active");
    if (!new Set(["included_in_income_tax", "separate_property_tax"]).has(treatment)) throw new DetailedFireTaxInputError("propertyRentalTaxTreatment is invalid");
    return treatment === "included_in_income_tax" ? subtractAmounts(annual, rental, "unique property annual tax") : annual;
  }

  function propertyAmounts(jurisdictions, treatment) {
    const active = jurisdictions.filter(function (jurisdiction) { return jurisdiction.property; });
    const uniqueAnnual = active.map(function (jurisdiction) { return uniquePropertyAnnualTax(jurisdiction.property, treatment); });
    const ownerCovered = active.map(function (jurisdiction) { return jurisdiction.property.retirementIntegration.ownerPropertyTaxAlreadyInLivingCosts; });
    const annualExpense = active.map(function (_jurisdiction, index) { return subtractAmounts(uniqueAnnual[index], ownerCovered[index], "property annual retirement expense"); });
    return {
      uniqueAnnual: addAmounts(uniqueAnnual, "property unique annual tax"),
      ownerCovered: addAmounts(ownerCovered, "owner property tax boundary"),
      annualExpense: addAmounts(annualExpense, "property annual tax expense"),
      oneTime: addAmounts(active.map(function (jurisdiction) { return jurisdiction.property.totals.oneTimeTax; }), "property one-time tax")
    };
  }

  function scenarioAudit(residence, destination, home) {
    const components = [residence, destination.credits, destination.property];
    if (home.enabled) components.push(home.credits, home.property);
    return {
      ruleIds: unique(components.flatMap(function (component) { return (component && component.ruleIds || []).concat(component && component.creditRuleIds || []); })
        .concat(destination.credits.categories.flatMap(function (category) { return (category.ruleIds || []).concat(category.creditRuleIds || []); }))
        .concat(home.enabled ? home.credits.categories.flatMap(function (category) { return (category.ruleIds || []).concat(category.creditRuleIds || []); }) : [])),
      sourceIds: unique(components.flatMap(function (component) { return (component && component.sourceIds || []).concat(component && component.creditSourceIds || []); })
        .concat(destination.credits.categories.flatMap(function (category) { return (category.sourceIds || []).concat(category.creditSourceIds || []); }))
        .concat(home.enabled ? home.credits.categories.flatMap(function (category) { return (category.sourceIds || []).concat(category.creditSourceIds || []); }) : [])),
      confidence: confidenceOf([destination.credits.confidence, destination.property.confidence]
        .concat(home.enabled ? [home.credits.confidence, home.property.confidence] : []))
    };
  }

  function assertUnifiedUnits(residence, destination, home, canonical) {
    const components = [destination.credits, destination.property, canonical];
    if (home.enabled) components.push(home.credits, home.property);
    const currencies = unique(components.map(function (component) { return component.currency; }));
    if (currencies.length !== 1) throw new DetailedFireTaxInputError("all detailed tax components must use one currency before totals are calculated");
    const taxYears = new Set(components.map(function (component) { return component.taxYear; }).concat([residence.taxYear]));
    if (taxYears.size !== 1) throw new DetailedFireTaxInputError("all detailed tax components must use one tax year before totals are calculated");
  }

  function scenarioResult(id, identity, residence, destination, home, canonical, retirement) {
    const destinationWithId = Object.assign({ branchId: id }, destination);
    const homeWithId = Object.assign({ branchId: id }, home);
    const reconciliation = reconcileIncome(destinationWithId, homeWithId, canonical);
    const property = propertyAmounts([destinationWithId].concat(home.enabled ? [homeWithId] : []), retirement.propertyRentalTaxTreatment);
    const treatmentTax = function (treatment) {
      return round(reconciliation.categories.filter(function (category) { return category.treatment === treatment; })
        .reduce(function (sum, category) { return sum + category.netTax; }, 0));
    };
    const dependableTax = treatmentTax("dependable_income");
    const returnCoveredTax = treatmentTax("return_covered");
    const incomeExpenseTax = treatmentTax("annual_expense");
    const grossDependableIncome = round(canonical.categories.filter(function (category) { return category.treatment === "dependable_income"; })
      .reduce(function (sum, category) { return sum + category.grossAmount; }, 0));
    const afterTaxDependableIncome = round(Math.max(0, grossDependableIncome - dependableTax));
    const annualTaxExpense = addAmounts([incomeExpenseTax, property.annualExpense], "retirement annual tax expense");
    const annualTax = addAmounts([reconciliation.totalNetIncomeTax, property.uniqueAnnual], "reconciled annual tax");
    const audit = scenarioAudit(residence, destinationWithId, homeWithId);
    const integration = {
      dependableIncomeTax: dependableTax,
      returnCoveredTax: returnCoveredTax,
      livingCostCoveredTax: property.ownerCovered,
      annualTaxExpense: annualTaxExpense,
      propertyRentalTaxTreatment: retirement.propertyRentalTaxTreatment || null,
      exclusions: [
        "Dependable-income tax is netted from the dependable income stream.",
        "Tax on return-covered income is represented by the selected after-fees-and-tax return.",
        "Owner property tax already included in living costs is not added again.",
        "Property value and equity remain outside liquid retirement income."
      ]
    };
    const projection = retirementUiApi().calculateDetailedRetirement(retirement.baseInput, {
      annualTaxExpenses: annualTaxExpense,
      afterTaxDependableIncome: afterTaxDependableIncome,
      selectedAfterTaxReturn: retirement.selectedAfterTaxReturn,
      returnBasis: retirement.returnBasis,
      dependableIncomeIndexed: retirement.dependableIncomeIndexed,
      dependableIncomeInflationRate: retirement.dependableIncomeInflationRate,
      planningRange: retirement.planningRange
    });
    return {
      id: id,
      branchIdentity: identity,
      residence: residence,
      destination: destinationWithId,
      continuingHome: homeWithId,
      globalReconciliation: reconciliation,
      totals: { annualTax: annualTax, oneTimeTaxes: property.oneTime, grossDependableIncome: grossDependableIncome, afterTaxDependableIncome: afterTaxDependableIncome },
      retirementIntegration: integration,
      taxAdjustedCapitalInput: projection.input,
      retirementProjection: Object.assign({ branchId: id }, projection),
      ruleIds: audit.ruleIds,
      sourceIds: audit.sourceIds,
      confidence: audit.confidence
    };
  }

  function aggregateCategory(branches, name) {
    if (branches.length === 1) return branches[0].category;
    const categories = branches.map(function (branch) { return branch.category; });
    const calculated = categories.filter(function (category) { return category.status === "calculated"; });
    const base = calculated[0] || categories[0];
    const result = Object.assign({}, base, {
      status: "conditional",
      branches: branches.map(function (branch) { return Object.assign({ branchId: branch.branchId }, branch.category); }),
      unresolvedFacts: unique(branches.flatMap(function (branch) { return branch.unresolvedFacts || []; })),
      formula: "Calculated each aligned detailed-tax scenario; displayed amounts are scenario minima and maxima.",
      assumptions: ["No residence or property branch was combined with an unrelated branch endpoint."],
      ruleIds: unique(categories.flatMap(function (category) { return category.ruleIds || []; })),
      sourceIds: unique(categories.flatMap(function (category) { return category.sourceIds || []; })),
      creditRuleIds: unique(categories.flatMap(function (category) { return category.creditRuleIds || []; })),
      creditSourceIds: unique(categories.flatMap(function (category) { return category.creditSourceIds || []; })),
      confidence: confidenceOf(categories.map(function (category) { return category.confidence; }))
    });
    AMOUNT_FIELDS.forEach(function (field) {
      const values = calculated.map(function (category) { return category[field]; }).filter(finiteAmount);
      result[field] = values.length ? rangeOf(values, name + "." + field) : null;
    });
    return result;
  }

  function aggregateCredits(seeds, key) {
    const entries = seeds.map(function (seed) { return { branchId: seed.id, result: seed[key].credits, unresolvedFacts: seed.residence.unresolvedFacts }; });
    if (entries.length === 1) return entries[0].result;
    const names = unique(entries.flatMap(function (entry) { return entry.result.categories.map(function (category) { return category.category; }); }));
    const categories = names.map(function (name) {
      return aggregateCategory(entries.map(function (entry) {
        return { branchId: entry.branchId, unresolvedFacts: entry.unresolvedFacts, category: entry.result.categories.find(function (category) { return category.category === name; }) };
      }).filter(function (entry) { return entry.category; }), name);
    });
    const field = function (name) { return rangeOf(entries.map(function (entry) { return entry.result[name]; }), "credits." + name); };
    return {
      status: "conditional", categories: categories, currency: entries[0].result.currency, taxYear: entries[0].result.taxYear,
      confidence: confidenceOf(entries.map(function (entry) { return entry.result.confidence; })),
      totalDomesticTax: field("totalDomesticTax"), totalSourceWithholding: field("totalSourceWithholding"),
      totalCreditsApplied: field("totalCreditsApplied"), totalNetTax: field("totalNetTax"),
      creditRuleIds: unique(entries.flatMap(function (entry) { return entry.result.creditRuleIds || []; })),
      creditSourceIds: unique(entries.flatMap(function (entry) { return entry.result.creditSourceIds || []; })),
      branches: entries.map(function (entry) { return { branchId: entry.branchId, result: entry.result }; })
    };
  }

  function emptyStage() { return { taxTotal: 0, nonTaxTotal: 0, prepaymentTotal: 0, lines: [] }; }

  function aggregateProperty(scenarios, key) {
    const entries = scenarios.map(function (scenario) { return { branchId: scenario.id, result: scenario[key].property }; });
    if (entries.length === 1) return entries[0].result;
    const stages = {};
    unique(entries.flatMap(function (entry) { return Object.keys(entry.result.stages); })).forEach(function (stage) {
      const stageEntries = entries.map(function (entry) { return { branchId: entry.branchId, stage: entry.result.stages[stage] || emptyStage() }; });
      stages[stage] = {
        taxTotal: rangeOf(stageEntries.map(function (entry) { return entry.stage.taxTotal; }), "property." + stage + ".taxTotal"),
        nonTaxTotal: rangeOf(stageEntries.map(function (entry) { return entry.stage.nonTaxTotal; }), "property." + stage + ".nonTaxTotal"),
        prepaymentTotal: rangeOf(stageEntries.map(function (entry) { return entry.stage.prepaymentTotal; }), "property." + stage + ".prepaymentTotal"),
        branchBreakdown: stageEntries.map(function (entry) { return Object.assign({ branchId: entry.branchId }, entry.stage); })
      };
    });
    const total = function (field) { return rangeOf(entries.map(function (entry) { return entry.result.totals[field]; }), "property.totals." + field); };
    return {
      status: "conditional", currency: entries[0].result.currency, taxYear: entries[0].result.taxYear, taxpayerScope: "conditional", stages: stages,
      totals: { annualTax: total("annualTax"), oneTimeTax: total("oneTimeTax"), allTax: total("allTax"), prepayments: total("prepayments"), nonTax: total("nonTax") },
      retirementIntegration: {
        annualTaxBeforeBoundary: rangeOf(entries.map(function (entry) { return entry.result.retirementIntegration.annualTaxBeforeBoundary; }), "property.retirement.annual"),
        ownerPropertyTaxAlreadyInLivingCosts: rangeOf(entries.map(function (entry) { return entry.result.retirementIntegration.ownerPropertyTaxAlreadyInLivingCosts; }), "property.retirement.owner"),
        additionalAnnualTaxExpense: rangeOf(entries.map(function (entry) { return entry.result.retirementIntegration.additionalAnnualTaxExpense; }), "property.retirement.additional"),
        excludedRuleIds: unique(entries.flatMap(function (entry) { return entry.result.retirementIntegration.excludedRuleIds || []; })),
        explanation: "Each displayed endpoint comes from a complete aligned detailed-tax scenario."
      },
      branches: entries.map(function (entry) { return Object.assign({ branchId: entry.branchId }, entry.result); }),
      ruleIds: unique(entries.flatMap(function (entry) { return entry.result.ruleIds || []; })),
      sourceIds: unique(entries.flatMap(function (entry) { return entry.result.sourceIds || []; })),
      confidence: confidenceOf(entries.map(function (entry) { return entry.result.confidence; })),
      assumptions: ["Ranges preserve aligned scenario identity; no independent component endpoints are summed."]
    };
  }

  function aggregateJurisdiction(seeds, scenarios, key) {
    const enabled = key === "destination" || seeds.some(function (seed) { return seed[key].enabled; });
    if (!enabled) return disabledHome();
    if (seeds.length === 1) return Object.assign({}, seeds[0][key], { property: aggregateProperty(scenarios, key) });
    const credits = aggregateCredits(seeds, key);
    return { enabled: key === "destination" ? undefined : true, incomeCategories: credits.categories, credits: credits, property: aggregateProperty(scenarios, key) };
  }

  function aggregateReconciliation(scenarios) {
    if (scenarios.length === 1) return scenarios[0].globalReconciliation;
    const fields = ["totalDomesticLiability", "totalUniqueWithholding", "totalCreditClaimed", "totalCreditApplied", "totalNetIncomeTax"];
    const result = { status: "conditional", branches: scenarios.map(function (scenario) { return { scenarioId: scenario.id, reconciliation: scenario.globalReconciliation }; }) };
    fields.forEach(function (field) { result[field] = rangeOf(scenarios.map(function (scenario) { return scenario.globalReconciliation[field]; }), "global reconciliation " + field); });
    result.withholdings = unique(scenarios.flatMap(function (scenario) { return scenario.globalReconciliation.withholdings.map(function (item) { return item.identity; }); }));
    return result;
  }

  function aggregateProjection(scenarios, planningRange) {
    if (scenarios.length === 1) return scenarios[0].retirementProjection;
    const ordered = scenarios.slice().sort(function (left, right) { return left.retirementProjection.refined.totalNeededToday - right.retirementProjection.refined.totalNeededToday; });
    return {
      status: "conditional",
      cases: { favorable: ordered[0].retirementProjection, adverse: ordered[ordered.length - 1].retirementProjection },
      branches: scenarios.map(function (scenario) { return { scenarioId: scenario.id, projection: scenario.retirementProjection }; }),
      capitalRange: { minimum: ordered[0].retirementProjection.refined.totalNeededToday, maximum: ordered[ordered.length - 1].retirementProjection.refined.totalNeededToday },
      planningRange: planningRange || null
    };
  }

  function conditionalInput(scenarios) {
    if (scenarios.length === 1) return scenarios[0].taxAdjustedCapitalInput;
    return {
      status: "conditional",
      cases: Object.fromEntries(scenarios.map(function (scenario) { return [scenario.id, scenario.taxAdjustedCapitalInput]; })),
      annualTaxExpenses: rangeOf(scenarios.map(function (scenario) { return scenario.retirementIntegration.annualTaxExpense; }), "capital input annual tax"),
      afterTaxDependableIncome: rangeOf(scenarios.map(function (scenario) { return scenario.totals.afterTaxDependableIncome; }), "capital input income"),
      returnBasis: "after_fees_and_tax"
    };
  }

  function calculateDetailedTax(profile, rules) {
    validateHeader(profile, rules);
    const residence = residenceApi().evaluateResidence(profile.residence, rules.residence.destination, rules.residence.home);
    const leaves = residenceLeaves(residence);
    const seeds = leaves.map(function (leaf, index) {
      const destination = calculateJurisdiction(profile.destination, leaf.residence, rules.destination);
      const home = profile.continuingHome && profile.continuingHome.enabled
        ? Object.assign({ enabled: true }, calculateJurisdiction(profile.continuingHome, leaf.residence, rules.continuingHome))
        : disabledHome();
      return { id: "residence-" + index, identity: leaf.identity, residence: leaf.residence, destination: destination, continuingHome: home };
    });
    const canonical = normalizedCanonicalIncome(seeds[0].destination, seeds[0].continuingHome, profile);
    seeds.forEach(function (seed) { assertUnifiedUnits(seed.residence, seed.destination, seed.continuingHome, canonical); });
    const scenarios = [];
    seeds.forEach(function (seed) {
      const destinationProperties = propertyLeaves(seed.destination.property);
      const homeProperties = seed.continuingHome.enabled ? propertyLeaves(seed.continuingHome.property) : [null];
      destinationProperties.forEach(function (destinationProperty, destinationIndex) {
        homeProperties.forEach(function (homeProperty, homeIndex) {
          const destinationFacts = destinationProperty.assumedFacts || {};
          const homeFacts = homeProperty && homeProperty.assumedFacts || {};
          if (!compatibleFacts(destinationFacts, homeFacts)) return;
          const id = [seed.id, "destination-property-" + destinationIndex, "home-property-" + homeIndex].join("|");
          const identity = Object.assign({}, seed.identity, { destinationPropertyFacts: destinationFacts, continuingHomePropertyFacts: homeFacts });
          const destination = Object.assign({}, seed.destination, { property: destinationProperty });
          const home = seed.continuingHome.enabled ? Object.assign({}, seed.continuingHome, { property: homeProperty }) : disabledHome();
          scenarios.push(scenarioResult(id, identity, seed.residence, destination, home, canonical, profile.retirement));
        });
      });
    });
    if (!scenarios.length) throw new DetailedFireTaxInputError("no compatible aligned residence and property scenarios remain");
    const destination = aggregateJurisdiction(seeds, scenarios, "destination");
    const home = aggregateJurisdiction(seeds, scenarios, "continuingHome");
    const projection = aggregateProjection(scenarios, profile.retirement.planningRange);
    const globalReconciliation = aggregateReconciliation(scenarios);
    const audit = {
      ruleIds: unique(scenarios.flatMap(function (scenario) { return scenario.ruleIds; })),
      sourceIds: unique(scenarios.flatMap(function (scenario) { return scenario.sourceIds; })),
      confidence: confidenceOf(scenarios.map(function (scenario) { return scenario.confidence; }))
    };
    const total = function (field) { return rangeOf(scenarios.map(function (scenario) { return scenario.totals[field]; }), "detailed totals " + field); };
    const integrationField = function (field) { return rangeOf(scenarios.map(function (scenario) { return scenario.retirementIntegration[field]; }), "retirement integration " + field); };
    const outerConditional = containsConditional({
      residence: residence,
      jurisdictions: seeds,
      retirementProjection: projection,
      globalReconciliation: globalReconciliation
    });
    return {
      status: outerConditional ? "conditional" : "calculated",
      currency: canonical.currency,
      taxYear: canonical.taxYear,
      residence: residence,
      canonicalIncome: canonical,
      destination: destination,
      continuingHome: home,
      scenarios: scenarios,
      globalReconciliation: globalReconciliation,
      totals: { annualTax: total("annualTax"), oneTimeTaxes: total("oneTimeTaxes"), grossDependableIncome: total("grossDependableIncome"), afterTaxDependableIncome: total("afterTaxDependableIncome") },
      afterTaxReturnBasis: { rate: profile.retirement.selectedAfterTaxReturn, basis: profile.retirement.returnBasis, formula: "User-selected portfolio return after fees and tax." },
      retirementIntegration: {
        dependableIncomeTax: integrationField("dependableIncomeTax"),
        returnCoveredTax: integrationField("returnCoveredTax"),
        livingCostCoveredTax: integrationField("livingCostCoveredTax"),
        annualTaxExpense: integrationField("annualTaxExpense"),
        propertyRentalTaxTreatment: profile.retirement.propertyRentalTaxTreatment || null,
        exclusions: scenarios[0].retirementIntegration.exclusions
      },
      taxAdjustedCapitalInput: conditionalInput(scenarios),
      retirementProjection: projection,
      ruleIds: audit.ruleIds,
      sourceIds: audit.sourceIds,
      confidence: audit.confidence
    };
  }

  return { calculateDetailedTax: calculateDetailedTax, DetailedFireTaxInputError: DetailedFireTaxInputError };
});
