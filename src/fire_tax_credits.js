(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxCredits = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

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
    return Array.from(new Set(values.filter(function (value) { return typeof value === "string" && value.length > 0; })));
  }

  function validateRules(rules) {
    if (!Array.isArray(rules)) throw new FireTaxCreditInputError("creditRules must be an array");
    rules.forEach(function (rule, index) {
      if (!record(rule) || rule.type !== "credit_limit" || typeof rule.id !== "string" || !Array.isArray(rule.source_ids) || rule.source_ids.length === 0 ||
          typeof rule.currency !== "string" || !/^[A-Z]{3}$/.test(rule.currency) ||
          !record(rule.formula) || rule.formula.operation !== "minimum" || !Array.isArray(rule.formula.operands) || rule.formula.operands.length !== 2 ||
          typeof rule.credit_operand !== "string" || typeof rule.limit_operand !== "string" || rule.formula.operands[0] !== rule.credit_operand || rule.formula.operands[1] !== rule.limit_operand ||
          rule.credit_basis !== "source_withholding" || !Number.isInteger(rule.order) || rule.order <= 0 ||
          !Array.isArray(rule.applies_to_categories) || rule.applies_to_categories.length === 0 || new Set(rule.applies_to_categories).size !== rule.applies_to_categories.length || !rule.applies_to_categories.every(function (category) { return typeof category === "string" && category.length > 0; })) {
        throw new FireTaxCreditInputError("creditRules[" + index + "] is not an executable validated credit limit");
      }
    });
    return rules.slice().sort(function (left, right) { return left.order - right.order || left.id.localeCompare(right.id); });
  }

  function validateCalculated(result, path) {
    ["domesticTax", "sourceWithholding", "netTax"].forEach(function (field) {
      if (!amount(result[field])) throw new FireTaxCreditInputError(path + "." + field + " must be a non-negative finite amount");
    });
    if (Math.abs(result.netTax - result.domesticTax - result.sourceWithholding) > 0.0000001) {
      throw new FireTaxCreditInputError(path + ".netTax must reconcile before credits");
    }
  }

  function validateResults(results) {
    if (!Array.isArray(results)) throw new FireTaxCreditInputError("categoryResults must be an array");
    const categories = new Set();
    results.forEach(function (result, index) {
      const path = "categoryResults[" + index + "]";
      if (!record(result) || typeof result.category !== "string" || result.category.length === 0 || categories.has(result.category) || typeof result.currency !== "string") {
        throw new FireTaxCreditInputError(path + " must identify one unique category and currency");
      }
      categories.add(result.category);
      if (result.status === "calculated") validateCalculated(result, path);
      else if (result.status === "conditional") {
        if (!Array.isArray(result.branches) || result.branches.length === 0) throw new FireTaxCreditInputError(path + ".branches must contain calculated alternatives");
        result.branches.forEach(function (branch, branchIndex) {
          if (!record(branch) || !["calculated", "out_of_scope"].includes(branch.status)) throw new FireTaxCreditInputError(path + ".branches[" + branchIndex + "] has an unsupported status");
          if (branch.status === "calculated") validateCalculated(branch, path + ".branches[" + branchIndex + "]");
        });
      } else if (result.status !== "out_of_scope") {
        throw new FireTaxCreditInputError(path + ".status is unsupported");
      }
    });
  }

  function rulesForCategory(rules, category) {
    return rules.filter(function (rule) { return rule.applies_to_categories.includes(category); });
  }

  function applyOne(result, rules) {
    if (result.status === "out_of_scope") {
      return Object.assign({}, result, { creditApplied: 0, creditRuleIds: [], creditSourceIds: [], creditFormula: "No tax amount is in scope for this branch." });
    }
    let remainingDomestic = result.domesticTax;
    let remainingWithholding = result.sourceWithholding;
    let creditApplied = 0;
    const matched = rulesForCategory(rules, result.category);
    matched.forEach(function (rule) {
      const credit = Math.min(remainingWithholding, remainingDomestic);
      creditApplied += credit;
      remainingWithholding -= credit;
      remainingDomestic -= credit;
    });
    return Object.assign({}, result, {
      creditApplied: round(creditApplied),
      netTax: round(result.domesticTax + result.sourceWithholding - creditApplied),
      creditRuleIds: matched.map(function (rule) { return rule.id; }),
      creditSourceIds: unique(matched.flatMap(function (rule) { return rule.source_ids; })),
      creditFormula: matched.length ? "Apply minimum(source withholding, remaining domestic tax) in validated rule order " + matched.map(function (rule) { return rule.order; }).join(", ") + "." : "No validated matching category credit rule."
    });
  }

  function valueRange(values) {
    return { minimum: Math.min.apply(Math, values), maximum: Math.max.apply(Math, values) };
  }

  function applyCategory(result, rules) {
    if (result.status !== "conditional") return applyOne(result, rules);
    const branches = result.branches.map(function (branch) {
      return applyOne(Object.assign({}, branch, { category: result.category, currency: result.currency }), rules);
    });
    const matched = rulesForCategory(rules, result.category);
    return Object.assign({}, result, {
      branches: branches,
      creditApplied: valueRange(branches.map(function (branch) { return branch.creditApplied; })),
      netTax: valueRange(branches.map(function (branch) { return amount(branch.netTax) ? branch.netTax : 0; })),
      creditRuleIds: matched.map(function (rule) { return rule.id; }),
      creditSourceIds: unique(matched.flatMap(function (rule) { return rule.source_ids; })),
      creditFormula: matched.length ? "Apply each validated category credit separately within each residence branch." : "No validated matching category credit rule."
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

  function applyForeignTaxCredits(categoryResults, creditRules) {
    validateResults(categoryResults);
    const orderedRules = validateRules(creditRules);
    const currencies = unique(categoryResults.map(function (result) { return result.currency; }).concat(orderedRules.map(function (rule) { return rule.currency; })));
    if (currencies.length > 1) throw new FireTaxCreditInputError("category results and credit rules must use one currency");
    const categories = categoryResults.map(function (result) { return applyCategory(result, orderedRules); });
    const unusedCredits = [];
    const unsupportedCredits = [];
    categories.forEach(function (category) {
      if (category.status !== "calculated" || category.sourceWithholding <= 0) return;
      const matched = rulesForCategory(orderedRules, category.category);
      if (matched.length === 0) {
        unsupportedCredits.push({
          category: category.category,
          amount: category.sourceWithholding,
          explanation: "Foreign tax is shown separately because no validated matching category credit rule applies."
        });
      } else if (category.sourceWithholding > category.creditApplied) {
        unusedCredits.push({
          category: category.category,
          amount: round(category.sourceWithholding - category.creditApplied),
          explanation: "Foreign tax exceeds the supported domestic category limit; the excess is not used against another category."
        });
      }
    });
    return {
      categories: categories,
      totalDomesticTax: sumField(categories, "domesticTax"),
      totalSourceWithholding: sumField(categories, "sourceWithholding"),
      totalCreditsApplied: sumField(categories, "creditApplied"),
      totalNetTax: sumField(categories, "netTax"),
      unusedCredits: unusedCredits,
      unsupportedCredits: unsupportedCredits,
      creditRuleIds: orderedRules.map(function (rule) { return rule.id; }),
      creditSourceIds: unique(orderedRules.flatMap(function (rule) { return rule.source_ids; }))
    };
  }

  return {
    applyForeignTaxCredits: applyForeignTaxCredits,
    FireTaxCreditInputError: FireTaxCreditInputError
  };
});
