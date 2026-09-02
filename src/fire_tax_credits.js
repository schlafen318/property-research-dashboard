(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxCredits = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const CONFIDENCE = ["low", "medium", "medium_high", "high"];
  const DEFINITE_SCOPES = new Set(["resident", "nonresident"]);

  class FireTaxCreditInputError extends Error {
    constructor(message) {
      super(message);
      this.name = "FireTaxCreditInputError";
    }
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function amount(value) {
    return typeof value === "number" && Number.isFinite(value) && value >= 0;
  }

  function round(value) {
    return Math.round((value + Number.EPSILON) * 100000000) / 100000000;
  }

  function unique(values) {
    return Array.from(new Set(values.filter(function (value) {
      return typeof value === "string" && value.length > 0;
    })));
  }

  function validStrings(values) {
    return Array.isArray(values) && values.length > 0 && values.every(function (value) {
      return typeof value === "string" && value.trim().length > 0;
    });
  }

  function lowestConfidence(values) {
    return values.reduce(function (lowest, value) {
      return CONFIDENCE.indexOf(value) < CONFIDENCE.indexOf(lowest) ? value : lowest;
    }, "high");
  }

  function validateRules(rules) {
    if (!Array.isArray(rules)) throw new FireTaxCreditInputError("creditRules must be an array");
    rules.forEach(function (rule, index) {
      const validYear = record(rule) && Number.isInteger(rule.tax_year) && rule.tax_year >= 2000 &&
        typeof rule.id === "string" && rule.id.endsWith("-" + rule.tax_year);
      if (!validYear || rule.type !== "credit_limit" || !validStrings(rule.source_ids) ||
          typeof rule.currency !== "string" || !/^[A-Z]{3}$/.test(rule.currency) ||
          !Array.isArray(rule.taxpayer_scope) || rule.taxpayer_scope.length === 0 || !rule.taxpayer_scope.every(function (scope) { return DEFINITE_SCOPES.has(scope); }) ||
          !CONFIDENCE.includes(rule.confidence) || !validStrings(rule.assumptions) || typeof rule.explanation !== "string" || rule.explanation.trim().length === 0 ||
          !record(rule.formula) || rule.formula.operation !== "minimum" || !Array.isArray(rule.formula.operands) || rule.formula.operands.length !== 2 ||
          typeof rule.credit_operand !== "string" || typeof rule.limit_operand !== "string" || rule.formula.operands[0] !== rule.credit_operand || rule.formula.operands[1] !== rule.limit_operand ||
          rule.credit_basis !== "source_withholding" || !Number.isInteger(rule.order) || rule.order <= 0 ||
          !Array.isArray(rule.applies_to_categories) || rule.applies_to_categories.length === 0 || new Set(rule.applies_to_categories).size !== rule.applies_to_categories.length || !rule.applies_to_categories.every(function (category) { return typeof category === "string" && category.length > 0; })) {
        throw new FireTaxCreditInputError("creditRules[" + index + "] is not an executable validated credit limit");
      }
    });
    return rules.slice().sort(function (left, right) {
      return left.order - right.order || left.id.localeCompare(right.id);
    });
  }

  function inheritedNode(node, parent) {
    const inherited = {};
    ["category", "currency", "taxYear", "confidence", "assumptions", "explanations", "ruleIds", "sourceIds"].forEach(function (field) {
      inherited[field] = Object.prototype.hasOwnProperty.call(node, field) ? node[field] : parent[field];
    });
    return Object.assign({}, node, inherited);
  }

  function validateAudit(node, path, conditionalAllowed) {
    if (typeof node.category !== "string" || node.category.length === 0 || typeof node.currency !== "string" || !/^[A-Z]{3}$/.test(node.currency) ||
        !Number.isInteger(node.taxYear) || node.taxYear < 2000 || !CONFIDENCE.includes(node.confidence) || !validStrings(node.assumptions) || !validStrings(node.explanations) ||
        !Array.isArray(node.ruleIds) || !Array.isArray(node.sourceIds) ||
        !(DEFINITE_SCOPES.has(node.taxpayerScope) || (conditionalAllowed && node.taxpayerScope === "conditional"))) {
      throw new FireTaxCreditInputError(path + " has incomplete category audit metadata");
    }
  }

  function validateCalculated(node, path) {
    ["domesticTax", "sourceWithholding", "netTax"].forEach(function (field) {
      if (!amount(node[field])) throw new FireTaxCreditInputError(path + "." + field + " must be a non-negative finite amount");
    });
    if (Math.abs(node.netTax - node.domesticTax - node.sourceWithholding) > 0.0000001) {
      throw new FireTaxCreditInputError(path + ".netTax must reconcile before credits");
    }
  }

  function validateOutOfScope(node, path) {
    ["domesticTax", "sourceWithholding", "netTax"].forEach(function (field) {
      if (node[field] !== null && node[field] !== 0) {
        throw new FireTaxCreditInputError(path + " out_of_scope " + field + " must be null or zero");
      }
    });
  }

  function leafValues(node, field) {
    if (node.status === "conditional") {
      return node.branches.flatMap(function (branch) { return leafValues(branch, field); });
    }
    if (node.status === "out_of_scope") return [0];
    return [node[field]];
  }

  function valueRange(values) {
    return {
      minimum: round(Math.min.apply(Math, values)),
      maximum: round(Math.max.apply(Math, values))
    };
  }

  function sameRange(actual, expected) {
    return record(actual) && amount(actual.minimum) && amount(actual.maximum) &&
      Math.abs(actual.minimum - expected.minimum) <= 0.0000001 &&
      Math.abs(actual.maximum - expected.maximum) <= 0.0000001;
  }

  function normalizeNode(rawNode, path, parent) {
    if (!record(rawNode)) throw new FireTaxCreditInputError(path + " must be an object");
    const node = inheritedNode(rawNode, parent || {});
    const conditional = node.status === "conditional";
    validateAudit(node, path, conditional);
    if (node.status === "calculated") {
      validateCalculated(node, path);
      return node;
    }
    if (node.status === "out_of_scope") {
      validateOutOfScope(node, path);
      return node;
    }
    if (!conditional || !Array.isArray(node.branches) || node.branches.length === 0) {
      throw new FireTaxCreditInputError(path + ".status or branches are unsupported");
    }
    node.branches = node.branches.map(function (branch, index) {
      return normalizeNode(branch, path + ".branches[" + index + "]", node);
    });
    ["domesticTax", "sourceWithholding", "netTax"].forEach(function (field) {
      const expected = valueRange(leafValues(node, field));
      if (!sameRange(node[field], expected)) {
        throw new FireTaxCreditInputError(path + "." + field + " must reconcile to its validated branches");
      }
      node[field] = expected;
    });
    return node;
  }

  function validateResults(results) {
    if (!Array.isArray(results)) throw new FireTaxCreditInputError("categoryResults must be an array");
    const categories = new Set();
    const normalized = results.map(function (result, index) {
      const node = normalizeNode(result, "categoryResults[" + index + "]", {});
      if (categories.has(node.category)) throw new FireTaxCreditInputError("categoryResults[" + index + "] duplicates a category");
      categories.add(node.category);
      return node;
    });
    const currencies = unique(normalized.map(function (result) { return result.currency; }));
    if (currencies.length > 1) throw new FireTaxCreditInputError("category results must use one currency");
    return normalized;
  }

  function rulesForResult(rules, result) {
    return rules.filter(function (rule) {
      return rule.applies_to_categories.includes(result.category) &&
        rule.tax_year === result.taxYear && rule.taxpayer_scope.includes(result.taxpayerScope);
    });
  }

  function applyOne(result, rules) {
    if (result.status === "out_of_scope") {
      return Object.assign({}, result, {
        creditApplied: 0, creditRuleIds: [], creditSourceIds: [], creditAssumptions: [],
        creditExplanations: ["No tax amount is in scope for this branch."],
        creditFormula: "No tax amount is in scope for this branch."
      });
    }
    const matched = rulesForResult(rules, result);
    if (matched.some(function (rule) { return rule.currency !== result.currency; })) {
      throw new FireTaxCreditInputError("applicable credit rules must match the category result currency");
    }
    let remainingDomestic = result.domesticTax;
    let remainingWithholding = result.sourceWithholding;
    let creditApplied = 0;
    matched.forEach(function () {
      const credit = Math.min(remainingWithholding, remainingDomestic);
      creditApplied += credit;
      remainingWithholding -= credit;
      remainingDomestic -= credit;
    });
    const creditAssumptions = unique(matched.flatMap(function (rule) { return rule.assumptions; }));
    const creditExplanations = matched.length ? matched.map(function (rule) { return rule.explanation; }) : ["No validated matching category credit rule."];
    return Object.assign({}, result, {
      creditApplied: round(creditApplied),
      netTax: round(result.domesticTax + result.sourceWithholding - creditApplied),
      confidence: lowestConfidence([result.confidence].concat(matched.map(function (rule) { return rule.confidence; }))),
      assumptions: unique(result.assumptions.concat(creditAssumptions)),
      creditRuleIds: matched.map(function (rule) { return rule.id; }),
      creditSourceIds: unique(matched.flatMap(function (rule) { return rule.source_ids; })),
      creditAssumptions: creditAssumptions,
      creditExplanations: creditExplanations,
      creditFormula: matched.length ? "Apply minimum(source withholding, remaining domestic tax) in validated rule order " + matched.map(function (rule) { return rule.order; }).join(", ") + "." : "No validated matching category credit rule."
    });
  }

  function applyCategory(result, rules) {
    if (result.status !== "conditional") return applyOne(result, rules);
    const branches = result.branches.map(function (branch) { return applyCategory(branch, rules); });
    return Object.assign({}, result, {
      branches: branches,
      creditApplied: valueRange(branches.flatMap(function (branch) { return leafValues(branch, "creditApplied"); })),
      netTax: valueRange(branches.flatMap(function (branch) { return leafValues(branch, "netTax"); })),
      confidence: lowestConfidence(branches.map(function (branch) { return branch.confidence; })),
      assumptions: unique(result.assumptions.concat(branches.flatMap(function (branch) { return branch.assumptions; }))),
      creditRuleIds: unique(branches.flatMap(function (branch) { return branch.creditRuleIds || []; })),
      creditSourceIds: unique(branches.flatMap(function (branch) { return branch.creditSourceIds || []; })),
      creditAssumptions: unique(branches.flatMap(function (branch) { return branch.creditAssumptions || []; })),
      creditExplanations: unique(branches.flatMap(function (branch) { return branch.creditExplanations || []; })),
      creditFormula: "Apply validated category credits independently within each residence branch."
    });
  }

  function sumField(categories, field) {
    let minimum = 0;
    let maximum = 0;
    let hasRange = false;
    categories.forEach(function (category) {
      const value = category[field];
      if (amount(value)) {
        minimum += value;
        maximum += value;
      } else if (record(value) && amount(value.minimum) && amount(value.maximum)) {
        hasRange = true;
        minimum += value.minimum;
        maximum += value.maximum;
      }
    });
    return hasRange ? { minimum: round(minimum), maximum: round(maximum) } : round(minimum);
  }

  function branchCreditAmounts(category, unsupported, inheritedAudit) {
    const assumptionPath = Array.isArray(inheritedAudit.assumptionPath) ? inheritedAudit.assumptionPath.slice() : [];
    if (Object.prototype.hasOwnProperty.call(category, "assumedValue")) {
      assumptionPath.push({
        assumedValue: category.assumedValue,
        residenceStatus: category.residenceStatus || null
      });
    }
    const audit = {
      assumedValue: Object.prototype.hasOwnProperty.call(category, "assumedValue") ? category.assumedValue : inheritedAudit.assumedValue,
      residenceStatus: category.residenceStatus || inheritedAudit.residenceStatus || null,
      assumptionPath: assumptionPath
    };
    if (category.status === "conditional") {
      return category.branches.flatMap(function (branch) { return branchCreditAmounts(branch, unsupported, audit); });
    }
    const source = category.status === "calculated" ? category.sourceWithholding : 0;
    const credit = category.status === "calculated" ? category.creditApplied : 0;
    const matched = Array.isArray(category.creditRuleIds) && category.creditRuleIds.length > 0;
    return [{
      assumedValue: audit.assumedValue, residenceStatus: audit.residenceStatus,
      assumptionPath: audit.assumptionPath,
      taxpayerScope: category.taxpayerScope, taxYear: category.taxYear,
      amount: round(unsupported ? (matched ? 0 : source) : (matched ? Math.max(0, source - credit) : 0))
    }];
  }

  function creditNote(category, unsupported) {
    const branches = branchCreditAmounts(category, unsupported, {});
    const values = branches.map(function (branch) { return branch.amount; });
    const maximum = Math.max.apply(Math, values);
    if (maximum <= 0) return null;
    return {
      category: category.category,
      amount: category.status === "conditional" ? valueRange(values) : maximum,
      branches: category.status === "conditional" ? branches : undefined,
      explanation: unsupported
        ? "Foreign tax is shown separately because no validated matching category credit rule applies in that branch."
        : "Foreign tax exceeds the supported domestic category limit; the excess is not used against another category."
    };
  }

  function applyForeignTaxCredits(categoryResults, creditRules) {
    const normalizedResults = validateResults(categoryResults);
    const orderedRules = validateRules(creditRules);
    const categories = normalizedResults.map(function (result) { return applyCategory(result, orderedRules); });
    const unusedCredits = categories.map(function (category) { return creditNote(category, false); }).filter(Boolean);
    const unsupportedCredits = categories.map(function (category) { return creditNote(category, true); }).filter(Boolean);
    return {
      categories: categories,
      currency: categories.length ? categories[0].currency : null,
      taxYear: categories.length && new Set(categories.map(function (category) { return category.taxYear; })).size === 1 ? categories[0].taxYear : null,
      confidence: lowestConfidence(categories.map(function (category) { return category.confidence; })),
      totalDomesticTax: sumField(categories, "domesticTax"),
      totalSourceWithholding: sumField(categories, "sourceWithholding"),
      totalCreditsApplied: sumField(categories, "creditApplied"),
      totalNetTax: sumField(categories, "netTax"),
      unusedCredits: unusedCredits,
      unsupportedCredits: unsupportedCredits,
      creditRuleIds: unique(categories.flatMap(function (category) { return category.creditRuleIds || []; })),
      creditSourceIds: unique(categories.flatMap(function (category) { return category.creditSourceIds || []; })),
      creditAssumptions: unique(categories.flatMap(function (category) { return category.creditAssumptions || []; })),
      creditExplanations: unique(categories.flatMap(function (category) { return category.creditExplanations || []; }))
    };
  }

  return { applyForeignTaxCredits: applyForeignTaxCredits, FireTaxCreditInputError: FireTaxCreditInputError };
});
