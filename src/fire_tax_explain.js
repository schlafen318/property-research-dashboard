(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxExplain = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function unique(values) {
    const seen = new Set();
    return (values || []).filter(function (value) {
      if (typeof value !== "string" || !value || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }

  function amountField(value) {
    return record(value) ? { amountRange: value } : { amount: value };
  }

  function auditLine(input) {
    return Object.assign({
      key: input.key,
      label: input.label,
      currency: input.currency,
      formula: input.formula,
      assumptions: unique(input.assumptions),
      exclusions: unique(input.exclusions),
      confidence: input.confidence,
      ruleIds: unique(input.ruleIds),
      sourceIds: unique(input.sourceIds),
      taxYear: input.taxYear
    }, amountField(input.value));
  }

  function categoryLine(category, jurisdictionLabel, result) {
    if (category.status === "out_of_scope" || category.netTax === null) return null;
    return auditLine({
      key: jurisdictionLabel + "_" + category.category,
      label: jurisdictionLabel + " — " + category.category.replace(/_/g, " "),
      value: category.netTax,
      currency: category.currency,
      formula: category.formula + "; " + (category.creditFormula || "no foreign-tax credit applied"),
      assumptions: (category.assumptions || []).concat(category.creditAssumptions || []),
      exclusions: ["Property lifecycle charges and non-tax costs are calculated separately."],
      confidence: category.confidence,
      ruleIds: (category.ruleIds || []).concat(category.creditRuleIds || []),
      sourceIds: (category.sourceIds || []).concat(category.creditSourceIds || []),
      taxYear: category.taxYear
    });
  }

  function propertyLines(property, jurisdictionLabel) {
    if (!property) return [];
    if (property.status === "conditional") {
      return Object.keys(property.stages).map(function (stage) {
        const value = property.stages[stage].taxTotal;
        return auditLine({
          key: jurisdictionLabel + "_property_" + stage,
          label: jurisdictionLabel + " property — " + stage,
          value: value,
          currency: property.currency,
          formula: "Calculated each validated property branch; displayed amount is the branch range for this lifecycle stage.",
          assumptions: property.assumptions,
          exclusions: ["Tax prepayments and non-tax compliance costs are displayed separately from tax liability."],
          confidence: property.confidence,
          ruleIds: property.ruleIds,
          sourceIds: property.sourceIds,
          taxYear: property.taxYear
        });
      });
    }
    return Object.values(property.stages).flatMap(function (stage) {
      return (stage.lines || []).filter(function (line) { return line.classification === "tax"; }).map(function (line) {
        return auditLine({
          key: jurisdictionLabel + "_property_" + line.stage + "_" + line.chargeKind,
          label: jurisdictionLabel + " property — " + line.label,
          value: line.amount,
          currency: line.currency,
          formula: line.formula,
          assumptions: line.assumptions,
          exclusions: ["Prepayments and non-tax charges are not included in this tax-liability line."],
          confidence: line.confidence,
          ruleIds: line.ruleIds,
          sourceIds: line.sourceIds,
          taxYear: line.taxYear
        });
      });
    });
  }

  function totalsSection(result) {
    const shared = {
      currency: result.currency,
      confidence: result.confidence,
      ruleIds: result.ruleIds,
      sourceIds: result.sourceIds,
      taxYear: result.taxYear
    };
    return {
      id: "reconciled_totals",
      label: "Reconciled totals",
      lines: [
        auditLine(Object.assign({}, shared, {
          key: "annual_tax",
          label: "Total annual tax",
          value: result.totals.annualTax,
          formula: "dependable-income tax + return-covered tax + living-cost-covered property tax + added annual tax expense",
          assumptions: ["Each supported annual liability is included once across destination and continuing-home overlays."],
          exclusions: ["One-time property taxes, tax prepayments, and non-tax costs."]
        })),
        auditLine(Object.assign({}, shared, {
          key: "one_time_taxes",
          label: "One-time property taxes",
          value: result.totals.oneTimeTaxes,
          formula: "purchase + sale + inheritance + gift tax liabilities across active jurisdictions",
          assumptions: ["Only selected active lifecycle stages are included."],
          exclusions: ["Annual taxes, prepayments, registration fees, and other non-tax costs."]
        })),
        auditLine(Object.assign({}, shared, {
          key: "after_tax_dependable_income",
          label: "After-tax dependable income",
          value: result.totals.afterTaxDependableIncome,
          formula: "gross dependable income - destination and continuing-home tax assigned to dependable categories",
          assumptions: ["The selected dependable categories are not portfolio returns."],
          exclusions: ["Portfolio income represented by the selected after-tax return and property equity."]
        }))
      ]
    };
  }

  function retirementSection(result) {
    const shared = {
      currency: result.currency,
      confidence: result.confidence,
      ruleIds: result.ruleIds,
      sourceIds: result.sourceIds,
      taxYear: result.taxYear
    };
    return {
      id: "retirement_integration",
      label: "Retirement projection inputs",
      lines: [
        auditLine(Object.assign({}, shared, {
          key: "added_annual_tax_expense",
          label: "Annual tax added to living expenses",
          value: result.retirementIntegration.annualTaxExpense,
          formula: "annual-expense-category tax + unique property tax not already in living costs or income tax",
          assumptions: ["The explicit category and property boundaries in the detailed profile are applied."],
          exclusions: result.retirementIntegration.exclusions
        })),
        auditLine(Object.assign({}, shared, {
          key: "selected_after_tax_return",
          label: "Selected after-tax portfolio return",
          value: result.afterTaxReturnBasis.rate,
          formula: result.afterTaxReturnBasis.formula,
          assumptions: ["Return basis is " + result.afterTaxReturnBasis.basis + "."],
          exclusions: ["Property appreciation and property equity are not liquid portfolio returns."],
          ruleIds: ["user-selected-after-tax-return"],
          sourceIds: ["user-supplied"]
        }))
      ]
    };
  }

  function jurisdictionSections(result, key, label) {
    const jurisdiction = result[key];
    if (!jurisdiction || jurisdiction.enabled === false) return [];
    return [
      {
        id: key + "_income",
        label: label + " income tax",
        lines: jurisdiction.credits.categories.map(function (category) {
          return categoryLine(category, label, result);
        }).filter(Boolean)
      },
      {
        id: key + "_property",
        label: label + " property tax",
        lines: propertyLines(jurisdiction.property, label)
      }
    ];
  }

  function explainCalculation(result) {
    if (!record(result) || !record(result.totals) || !record(result.retirementIntegration)) {
      throw new TypeError("DetailedTaxResult is required");
    }
    return jurisdictionSections(result, "destination", "Destination")
      .concat(jurisdictionSections(result, "continuingHome", "Continuing home"))
      .concat([totalsSection(result), retirementSection(result)]);
  }

  return { explainCalculation: explainCalculation };
});
