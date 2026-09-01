(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxIncome = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const INCOME_TYPES = new Set(["rate_band", "allowance", "withholding"]);
  const SCOPES = new Set(["worldwide_income", "source_income", "conditional"]);
  const CONFIDENCE = ["low", "medium", "medium_high", "high"];

  class FireTaxIncomeInputError extends Error {
    constructor(message) {
      super(message);
      this.name = "FireTaxIncomeInputError";
    }
  }

  class FireTaxIncomeRuleError extends Error {
    constructor(message) {
      super(message);
      this.name = "FireTaxIncomeRuleError";
    }
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function money(value) {
    return typeof value === "number" && Number.isFinite(value) && value >= 0;
  }

  function unique(values) {
    return Array.from(new Set(values.filter(function (value) {
      return typeof value === "string" && value.length > 0;
    })));
  }

  function round(value) {
    return Math.round((value + Number.EPSILON) * 100000000) / 100000000;
  }

  function selectBundle(payload) {
    if (!record(payload) || payload.schema_version !== 1 || !Number.isInteger(payload.tax_year) || !record(payload.operand_catalog) || !record(payload.jurisdictions)) {
      throw new FireTaxIncomeRuleError("rules must be a validated Task 1 rule payload");
    }
    const keys = Object.keys(payload.jurisdictions);
    const jurisdictionId = typeof payload.active_jurisdiction_id === "string"
      ? payload.active_jurisdiction_id
      : keys.length === 1 ? keys[0] : null;
    const jurisdiction = jurisdictionId ? payload.jurisdictions[jurisdictionId] : null;
    if (!record(jurisdiction) || jurisdiction.id !== jurisdictionId || !Array.isArray(jurisdiction.rules)) {
      throw new FireTaxIncomeRuleError("active jurisdiction must identify a validated rule graph");
    }
    const side = jurisdiction.calculation_side;
    if (side !== "destination" && side !== "home") {
      throw new FireTaxIncomeRuleError("jurisdiction calculation_side must be destination or home");
    }
    if (!Array.isArray(payload.sources) || payload.sources.length === 0) {
      throw new FireTaxIncomeRuleError("rules must include source audit records");
    }
    const sourceIds = new Set(payload.sources.map(function (source) { return record(source) ? source.id : null; }));
    if (sourceIds.has(null) || sourceIds.size !== payload.sources.length) {
      throw new FireTaxIncomeRuleError("rules contain invalid or duplicate sources");
    }
    return { payload: payload, jurisdiction: jurisdiction, jurisdictionId: jurisdictionId, side: side, sourceIds: sourceIds };
  }

  function validateAudit(rule, bundle) {
    return record(rule) && typeof rule.id === "string" && rule.id.endsWith("-" + bundle.payload.tax_year) &&
      rule.tax_year === bundle.payload.tax_year && typeof rule.category === "string" && rule.category.length > 0 &&
      typeof rule.currency === "string" && /^[A-Z]{3}$/.test(rule.currency) &&
      Array.isArray(rule.taxpayer_scope) && rule.taxpayer_scope.length > 0 && rule.taxpayer_scope.every(function (scope) { return scope === "resident" || scope === "nonresident"; }) &&
      Array.isArray(rule.source_ids) && rule.source_ids.length > 0 && rule.source_ids.every(function (id) { return bundle.sourceIds.has(id); }) &&
      typeof rule.explanation === "string" && rule.explanation.trim().length > 0 && CONFIDENCE.includes(rule.confidence);
  }

  function validateBands(rule) {
    if (!Array.isArray(rule.bands) || rule.bands.length === 0 || !record(rule.formula) || rule.formula.operation !== "progressive_rate" || !Array.isArray(rule.formula.operands) || rule.formula.operands.length !== 1) return false;
    let expectedFrom = 0;
    for (let index = 0; index < rule.bands.length; index += 1) {
      const band = rule.bands[index];
      if (!record(band) || !money(band.from) || band.from !== expectedFrom || typeof band.rate !== "number" || !Number.isFinite(band.rate) || band.rate < 0 || band.rate > 1) return false;
      if (band.up_to === null) {
        if (index !== rule.bands.length - 1) return false;
        expectedFrom = null;
      } else if (!money(band.up_to) || band.up_to <= band.from) {
        return false;
      } else {
        expectedFrom = band.up_to;
      }
    }
    return expectedFrom === null;
  }

  function operand(bundle, operandId, kind, valueType) {
    const candidate = bundle.payload.operand_catalog[operandId];
    if (!record(candidate) || candidate.kind !== kind || candidate.value_type !== valueType) {
      throw new FireTaxIncomeRuleError("formula operand " + operandId + " is not an executable " + kind + " " + valueType + " operand");
    }
    return candidate;
  }

  function validateRateRule(rule, bundle) {
    if (!validateAudit(rule, bundle) || !validateBands(rule)) {
      throw new FireTaxIncomeRuleError("rate rule " + String(rule && rule.id) + " has invalid bands or audit metadata");
    }
    const grossOperand = operand(bundle, rule.formula.operands[0], "profile", "money");
    if (grossOperand.currency !== rule.currency || typeof grossOperand.profile_key !== "string") {
      throw new FireTaxIncomeRuleError("rate rule " + rule.id + " has a currency or profile operand mismatch");
    }
    if (rule.category === "retirement_account_withdrawal") {
      const classification = operand(bundle, rule.account_classification_operand, "profile", "string");
      if (!Array.isArray(classification.allowed_values) || !Array.isArray(rule.supported_account_classifications) || rule.supported_account_classifications.length === 0 || !rule.supported_account_classifications.every(function (value) { return classification.allowed_values.includes(value); })) {
        throw new FireTaxIncomeRuleError("retirement-account classification allowlist is invalid");
      }
    }
    return grossOperand;
  }

  function validateAllowance(rule, rateRule, bundle) {
    if (!validateAudit(rule, bundle) || !record(rule.formula) || !["minimum", "maximum"].includes(rule.formula.operation) || !Array.isArray(rule.formula.operands) || rule.formula.operands.length !== 2 || !money(rule.amount)) {
      throw new FireTaxIncomeRuleError("allowance rule " + String(rule && rule.id) + " is invalid");
    }
    if (rule.currency !== rateRule.currency || rule.formula.operands[0] !== rateRule.formula.operands[0] || rule.formula.operands[1] !== rule.amount_operand) {
      throw new FireTaxIncomeRuleError("allowance rule " + rule.id + " is not linked to its category amount");
    }
    const amountOperand = operand(bundle, rule.amount_operand, "constant", "money");
    if (amountOperand.currency !== rule.currency || amountOperand.value !== rule.amount) {
      throw new FireTaxIncomeRuleError("allowance rule " + rule.id + " amount does not match its constant");
    }
  }

  function validateWithholding(rule, rateRule, bundle) {
    if (!validateAudit(rule, bundle) || !record(rule.formula) || rule.formula.operation !== "multiply" || !Array.isArray(rule.formula.operands) || rule.formula.operands.length !== 2 || typeof rule.rate !== "number" || !Number.isFinite(rule.rate) || rule.rate < 0 || rule.rate > 1) {
      throw new FireTaxIncomeRuleError("withholding rule " + String(rule && rule.id) + " is invalid");
    }
    if (rule.currency !== rateRule.currency || rule.formula.operands[0] !== rateRule.formula.operands[0] || rule.formula.operands[1] !== rule.rate_operand) {
      throw new FireTaxIncomeRuleError("withholding rule " + rule.id + " is not linked to its category amount");
    }
    const rateOperand = operand(bundle, rule.rate_operand, "constant", "number");
    if (rateOperand.value !== rule.rate) {
      throw new FireTaxIncomeRuleError("withholding rule " + rule.id + " rate does not match its constant");
    }
  }

  function projection(payload) {
    const bundle = selectBundle(payload);
    const incomeRules = bundle.jurisdiction.rules.filter(function (rule) { return record(rule) && INCOME_TYPES.has(rule.type); });
    const rateRules = incomeRules.filter(function (rule) { return rule.type === "rate_band"; });
    const seen = new Set();
    const categories = rateRules.map(function (rateRule) {
      if (seen.has(rateRule.category)) throw new FireTaxIncomeRuleError("multiple rate rules exist for category " + rateRule.category);
      seen.add(rateRule.category);
      const grossOperand = validateRateRule(rateRule, bundle);
      const allowances = incomeRules.filter(function (rule) { return rule.type === "allowance" && rule.category === rateRule.category; });
      const withholding = incomeRules.filter(function (rule) { return rule.type === "withholding" && rule.category === rateRule.category; });
      allowances.forEach(function (rule) { validateAllowance(rule, rateRule, bundle); });
      withholding.forEach(function (rule) { validateWithholding(rule, rateRule, bundle); });
      return { rateRule: rateRule, grossOperand: grossOperand, allowances: allowances, withholding: withholding };
    });
    if (categories.length === 0) throw new FireTaxIncomeRuleError("active jurisdiction has no executable income rate rules");
    return Object.assign(bundle, { categories: categories });
  }

  function validateProfile(profile, bundle) {
    if (!record(profile)) throw new FireTaxIncomeInputError("profile must be an object");
    if (profile.taxYear !== bundle.payload.tax_year) throw new FireTaxIncomeInputError("profile taxYear must match the validated rule year");
    const currencies = unique(bundle.categories.map(function (category) { return category.rateRule.currency; }));
    if (currencies.length !== 1 || profile.currency !== currencies[0]) throw new FireTaxIncomeInputError("profile currency must match the active income rules");
    if (!record(profile.incomeSourceJurisdictions)) throw new FireTaxIncomeInputError("incomeSourceJurisdictions must identify each income source");
    bundle.categories.forEach(function (category) {
      const key = category.grossOperand.profile_key;
      if (!money(profile[key])) throw new FireTaxIncomeInputError(key + " must be a non-negative finite amount");
      const source = profile.incomeSourceJurisdictions[category.rateRule.category];
      if (typeof source !== "string" || source.length === 0) throw new FireTaxIncomeInputError("incomeSourceJurisdictions." + category.rateRule.category + " is required");
      if (category.rateRule.category === "retirement_account_withdrawal") {
        const classificationOperand = bundle.payload.operand_catalog[category.rateRule.account_classification_operand];
        const classification = profile[classificationOperand.profile_key];
        if (!category.rateRule.supported_account_classifications.includes(classification)) {
          throw new FireTaxIncomeInputError(classificationOperand.profile_key + " is unsupported by the validated retirement-account rule");
        }
      }
    });
  }

  function progressiveTax(amount, bands) {
    let tax = 0;
    bands.forEach(function (band) {
      const upper = band.up_to === null ? amount : Math.min(amount, band.up_to);
      const slice = Math.max(0, upper - band.from);
      tax += slice * band.rate;
    });
    return round(tax);
  }

  function confidenceFor(rules) {
    return rules.reduce(function (lowest, rule) {
      return CONFIDENCE.indexOf(rule.confidence) < CONFIDENCE.indexOf(lowest) ? rule.confidence : lowest;
    }, "high");
  }

  function scopeFor(residence, side) {
    if (!record(residence) || !record(residence.scopes) || !SCOPES.has(residence.scopes[side])) {
      throw new FireTaxIncomeInputError("residence must contain a supported " + side + " income scope");
    }
    return residence.scopes[side];
  }

  function calculateCategory(profile, residence, bundle, category) {
    const scope = scopeFor(residence, bundle.side);
    if (scope === "conditional") throw new FireTaxIncomeInputError("conditional residence requires calculated branches");
    const taxpayerScope = scope === "worldwide_income" ? "resident" : "nonresident";
    const rateRule = category.rateRule;
    if (!rateRule.taxpayer_scope.includes(taxpayerScope)) {
      throw new FireTaxIncomeRuleError("no " + taxpayerScope + " rule is validated for " + rateRule.category);
    }
    const gross = profile[category.grossOperand.profile_key];
    const source = profile.incomeSourceJurisdictions[rateRule.category];
    const included = scope === "worldwide_income" || source === bundle.jurisdictionId || source === bundle.side;
    const allRules = [rateRule].concat(category.allowances, category.withholding);
    const audit = {
      taxYear: rateRule.tax_year,
      currency: rateRule.currency,
      taxpayerScope: taxpayerScope,
      confidence: confidenceFor(allRules),
      ruleIds: allRules.map(function (rule) { return rule.id; }),
      sourceIds: unique(allRules.flatMap(function (rule) { return rule.source_ids; })),
      exempt: rateRule.no_tax === true,
      assumptions: ["Income amounts and source jurisdiction are supplied by the user.", "All category amounts use " + rateRule.currency + " for tax year " + rateRule.tax_year + "."]
    };
    if (!included) {
      return Object.assign({
        category: rateRule.category,
        status: "out_of_scope",
        grossIncome: gross,
        deductions: null,
        taxableBase: null,
        domesticTax: null,
        sourceWithholding: null,
        netTax: null,
        formula: "Not calculated because the active rule scope includes only locally sourced income.",
        explanations: ["The income source is outside the active jurisdiction; this is an out-of-scope result, not a zero-tax claim."]
      }, audit);
    }
    const deductions = round(Math.min(gross, category.allowances.reduce(function (sum, rule) { return sum + rule.amount; }, 0)));
    const taxableBase = round(Math.max(0, gross - deductions));
    const domesticTax = progressiveTax(taxableBase, rateRule.bands);
    const sourceWithholding = round(category.withholding.reduce(function (sum, rule) { return sum + gross * rule.rate; }, 0));
    const netTax = round(domesticTax + sourceWithholding);
    const formulaParts = ["gross " + gross + " - allowance " + deductions + " = taxable base " + taxableBase, "progressive bands = domestic tax " + domesticTax];
    if (category.withholding.length) formulaParts.push("gross × source withholding rate = " + sourceWithholding);
    return Object.assign({
      category: rateRule.category,
      status: "calculated",
      grossIncome: gross,
      deductions: deductions,
      taxableBase: taxableBase,
      domesticTax: domesticTax,
      sourceWithholding: sourceWithholding,
      netTax: netTax,
      formula: formulaParts.join("; "),
      explanations: allRules.map(function (rule) { return rule.explanation; })
    }, audit);
  }

  function range(values) {
    return { minimum: Math.min.apply(Math, values), maximum: Math.max.apply(Math, values) };
  }

  function conditionalCategory(profile, residence, bundle, category) {
    if (!Array.isArray(residence.branches) || residence.branches.length === 0) {
      throw new FireTaxIncomeInputError("conditional residence requires calculated branches");
    }
    const branches = residence.branches.map(function (branch) {
      const result = calculateCategory(profile, branch, bundle, category);
      return Object.assign({}, result, {
        assumedValue: Object.prototype.hasOwnProperty.call(branch, "assumedValue") ? branch.assumedValue : null,
        residenceStatus: branch.status || null
      });
    });
    const amountFields = ["grossIncome", "deductions", "taxableBase", "domesticTax", "sourceWithholding", "netTax"];
    const amounts = {};
    amountFields.forEach(function (field) {
      amounts[field] = range(branches.map(function (branch) { return money(branch[field]) ? branch[field] : 0; }));
    });
    return Object.assign({
      category: category.rateRule.category,
      status: "conditional",
      branches: branches,
      unresolvedFacts: Array.isArray(residence.unresolvedFacts) ? unique(residence.unresolvedFacts) : [],
      formula: "Calculated each supported residence branch; displayed amounts are branch minima and maxima.",
      explanations: ["No residence branch was selected without the controlling fact."]
    }, amounts, {
      taxYear: category.rateRule.tax_year,
      currency: category.rateRule.currency,
      taxpayerScope: "conditional",
      confidence: confidenceFor([category.rateRule].concat(category.allowances, category.withholding)),
      ruleIds: unique(branches.flatMap(function (branch) { return branch.ruleIds; })),
      sourceIds: unique(branches.flatMap(function (branch) { return branch.sourceIds; })),
      exempt: category.rateRule.no_tax === true,
      assumptions: ["Each displayed endpoint is calculated from a supported residence branch."]
    });
  }

  function splitYearAlternatives(residence, side) {
    if (!Array.isArray(residence.periods) || residence.periods.length < 2) return null;
    const branches = [];
    const seen = new Set();
    residence.periods.forEach(function (period) {
      if (!record(period) || !record(period.scopes) || !SCOPES.has(period.scopes[side]) || period.scopes[side] === "conditional") return;
      const key = period.scopes[side];
      if (seen.has(key)) return;
      seen.add(key);
      branches.push({ status: period.status || null, scopes: period.scopes, assumedValue: key });
    });
    return branches.length > 1 ? branches : null;
  }

  function calculateIncomeTax(profile, residence, rules) {
    const bundle = projection(rules);
    validateProfile(profile, bundle);
    const scope = scopeFor(residence, bundle.side);
    if (scope === "conditional" || residence.status === "conditional") {
      return bundle.categories.map(function (category) { return conditionalCategory(profile, residence, bundle, category); });
    }
    const periodBranches = splitYearAlternatives(residence, bundle.side);
    if (periodBranches) {
      const splitResidence = {
        status: "conditional",
        scopes: { destination: "conditional", home: "conditional" },
        unresolvedFacts: ["incomeTimingAcrossResidencePeriods"],
        branches: periodBranches
      };
      return bundle.categories.map(function (category) {
        const result = conditionalCategory(profile, splitResidence, bundle, category);
        result.explanations = ["Income timing across the supported residence periods is unknown, so the result spans the calculated scope endpoints without assuming a proration."];
        return result;
      });
    }
    return bundle.categories.map(function (category) { return calculateCategory(profile, residence, bundle, category); });
  }

  return {
    calculateIncomeTax: calculateIncomeTax,
    FireTaxIncomeInputError: FireTaxIncomeInputError,
    FireTaxIncomeRuleError: FireTaxIncomeRuleError
  };
});
