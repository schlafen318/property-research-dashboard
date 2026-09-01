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
    const line = Object.assign({
      key: input.key,
      label: input.label,
      currency: input.currency,
      formula: input.formula,
      assumptions: unique(input.assumptions),
      exclusions: unique(input.exclusions),
      confidence: input.confidence,
      ruleIds: unique(input.ruleIds),
      sourceIds: unique(input.sourceIds),
      taxYear: input.taxYear,
      branchIds: unique(input.branchIds)
    }, amountField(input.value));
    if (input.notApplicable === true) line.notApplicable = true;
    if (record(input.endpointScenarioIds)) line.endpointScenarioIds = input.endpointScenarioIds;
    return line;
  }

  function allScenarioIds(result) {
    return (result.scenarioTuples || []).map(function (item) { return item.scenarioId; });
  }

  function endpointScenarioIds(result, field, value) {
    if (!record(value)) return undefined;
    const tuples = result.scenarioTuples || [];
    return {
      minimum: tuples.filter(function (tuple) { return tuple[field] === value.minimum; }).map(function (tuple) { return tuple.scenarioId; }),
      maximum: tuples.filter(function (tuple) { return tuple[field] === value.maximum; }).map(function (tuple) { return tuple.scenarioId; })
    };
  }

  function expandedBranchIds(result, branchId) {
    return allScenarioIds(result).filter(function (scenarioId) {
      return scenarioId === branchId || scenarioId.indexOf(branchId + "|") === 0;
    });
  }

  function branchEndpointIds(result, branches, field, value) {
    if (!record(value) || !Array.isArray(branches)) return undefined;
    const ids = function (endpoint) {
      return unique(branches.filter(function (branch) { return branch[field] === value[endpoint]; })
        .flatMap(function (branch) { return expandedBranchIds(result, branch.branchId); }));
    };
    return { minimum: ids("minimum"), maximum: ids("maximum") };
  }

  function categoryLine(category, jurisdictionLabel, result) {
    if (category.status === "out_of_scope" || category.domesticTax === null) return null;
    return auditLine({
      key: jurisdictionLabel + "_" + category.category,
      label: jurisdictionLabel + " domestic liability — " + category.category.replace(/_/g, " "),
      value: category.domesticTax,
      currency: category.currency,
      formula: category.formula + "; matching tax payments and foreign-tax credits are allocated only in the global reconciliation",
      assumptions: category.assumptions || [],
      exclusions: ["Tax payments, foreign-tax credits, property lifecycle charges, and non-tax costs are calculated separately."],
      confidence: category.confidence,
      ruleIds: category.ruleIds || [],
      sourceIds: category.sourceIds || [],
      taxYear: category.taxYear,
      branchIds: allScenarioIds(result),
      endpointScenarioIds: branchEndpointIds(result, category.branches, "domesticTax", category.domesticTax)
    });
  }

  function propertyLines(property, jurisdictionLabel, result) {
    if (!property) return [];
    if (property.taxpayerScope === "not_applicable") {
      return [auditLine({
        key: jurisdictionLabel + "_property_not_applicable",
        label: jurisdictionLabel + " owned-property calculation",
        value: null,
        currency: property.currency,
        formula: "Owned-property calculation not applicable; include renter municipal/housing fees in annual spending.",
        assumptions: property.assumptions || ["The live plan contains no owned property or property income."],
        exclusions: ["No zero-tax owned-property conclusion is made."],
        confidence: property.confidence,
        ruleIds: [], sourceIds: [], taxYear: property.taxYear,
        notApplicable: true,
      })];
    }
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
          taxYear: property.taxYear,
          branchIds: allScenarioIds(result),
          endpointScenarioIds: branchEndpointIds(result, property.stages[stage].branchBreakdown, "taxTotal", value)
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
          taxYear: line.taxYear,
          branchIds: allScenarioIds(result)
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
      taxYear: result.taxYear,
      branchIds: allScenarioIds(result)
    };
    const propertyOverlays = [result.destination && result.destination.property, result.continuingHome && result.continuingHome.property].filter(record);
    const propertyNotApplicable = propertyOverlays.length > 0 && propertyOverlays.every(function (property) { return property.taxpayerScope === "not_applicable"; });
    const lines = [
      auditLine(Object.assign({}, shared, {
        key: "annual_tax",
        label: "Total annual tax",
        value: result.totals.annualTax,
        formula: "dependable-income tax netted from income + return-covered tax + living-cost-covered property tax + added annual tax expense including any excess dependable tax",
        assumptions: ["Each supported annual liability is included once across destination and continuing-home overlays."],
        exclusions: ["One-time property taxes, tax payments already withheld, and non-tax costs."],
        endpointScenarioIds: endpointScenarioIds(result, "annualTax", result.totals.annualTax)
      }))
    ];
    if (!propertyNotApplicable) lines.push(auditLine(Object.assign({}, shared, {
      key: "one_time_taxes",
      label: "One-time property taxes",
      value: result.totals.oneTimeTaxes,
      formula: "purchase + sale + inheritance + gift tax liabilities across active jurisdictions",
      assumptions: ["Only selected active lifecycle stages are included."],
      exclusions: ["Annual taxes, prepayments, registration fees, and other non-tax costs."],
      endpointScenarioIds: endpointScenarioIds(result, "oneTimeTaxes", result.totals.oneTimeTaxes)
    })));
    lines.push(auditLine(Object.assign({}, shared, {
      key: "after_tax_dependable_income",
      label: "After-tax dependable income",
      value: result.totals.afterTaxDependableIncome,
      formula: "gross dependable income - minimum(gross dependable income, dependable-income tax liability)",
      assumptions: ["The selected dependable categories are not portfolio returns; tax beyond their gross income is moved to annual expense."],
      exclusions: ["Portfolio income represented by the selected after-tax return and property equity."],
      endpointScenarioIds: endpointScenarioIds(result, "afterTaxDependableIncome", result.totals.afterTaxDependableIncome)
    })));
    return {
      id: "reconciled_totals",
      label: "Reconciled totals",
      lines: lines
    };
  }

  function retirementSection(result) {
    const shared = {
      currency: result.currency,
      confidence: result.confidence,
      ruleIds: result.ruleIds,
      sourceIds: result.sourceIds,
      taxYear: result.taxYear,
      branchIds: allScenarioIds(result)
    };
    return {
      id: "retirement_integration",
      label: "Retirement projection inputs",
      lines: [
        auditLine(Object.assign({}, shared, {
          key: "dependable_income_tax_liability",
          label: "Dependable-income tax liability",
          value: result.retirementIntegration.dependableIncomeTax,
          formula: "sum of annual tax liability assigned to dependable-income categories",
          assumptions: ["This is the full liability before dividing it between income netting and annual expense."],
          exclusions: ["Return-covered tax, property tax, and annual-expense-category tax."],
          endpointScenarioIds: endpointScenarioIds(result, "dependableIncomeTax", result.retirementIntegration.dependableIncomeTax)
        })),
        auditLine(Object.assign({}, shared, {
          key: "dependable_tax_netted_from_income",
          label: "Dependable tax netted from income",
          value: result.retirementIntegration.dependableIncomeTaxNetted,
          formula: "minimum(gross dependable income, dependable-income tax liability)",
          assumptions: ["After-tax dependable income cannot fall below zero."],
          exclusions: ["Any dependable tax above gross dependable income; that excess is added to annual expense."],
          endpointScenarioIds: endpointScenarioIds(result, "dependableIncomeTaxNetted", result.retirementIntegration.dependableIncomeTaxNetted)
        })),
        auditLine(Object.assign({}, shared, {
          key: "excess_dependable_tax_expense",
          label: "Excess dependable tax added to expenses",
          value: result.retirementIntegration.excessDependableIncomeTax,
          formula: "maximum(0, dependable-income tax liability - gross dependable income)",
          assumptions: ["The excess is included exactly once in annual tax expense."],
          exclusions: ["The portion already netted from dependable income."],
          endpointScenarioIds: endpointScenarioIds(result, "excessDependableIncomeTax", result.retirementIntegration.excessDependableIncomeTax)
        })),
        auditLine(Object.assign({}, shared, {
          key: "added_annual_tax_expense",
          label: "Annual tax added to living expenses",
          value: result.retirementIntegration.annualTaxExpense,
          formula: "annual-expense-category tax + unique property tax not already in living costs or income tax + excess dependable-income tax",
          assumptions: ["The explicit category and property boundaries in the detailed profile are applied."],
          exclusions: result.retirementIntegration.exclusions,
          endpointScenarioIds: endpointScenarioIds(result, "annualTaxExpense", result.retirementIntegration.annualTaxExpense)
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

  function reconciliationSection(result) {
    const scenarios = result.scenarios || [];
    const shared = {
      currency: result.currency,
      confidence: result.confidence,
      ruleIds: result.ruleIds,
      sourceIds: result.sourceIds,
      taxYear: result.taxYear
    };
    const definitions = [
      {
        key: "annual_income_tax_liability",
        label: "Annual income-tax liability",
        field: "totalAnnualIncomeTaxLiability",
        auditCollections: ["liabilities", "credits"],
        formula: "gross destination and source-jurisdiction liabilities - allocated foreign-tax credits",
        exclusions: ["Tax payments already withheld and property tax liabilities."]
      },
      {
        key: "tax_payments_already_withheld",
        label: "Tax payments already withheld",
        field: "totalTaxPayments",
        auditCollections: ["payments"],
        formula: "unique source-jurisdiction withholding collected once; applied and excess amounts remain separate in the payment audit",
        exclusions: ["Unpaid liability and foreign-tax credits."]
      },
      {
        key: "foreign_tax_credits_applied",
        label: "Foreign-tax credits applied",
        field: "totalCreditApplied",
        auditCollections: ["credits"],
        formula: "foreign tax paid allocated only against the matching other-jurisdiction category liability",
        exclusions: ["Source-jurisdiction tax payments and unused credit claims."]
      },
      {
        key: "remaining_income_tax_balance",
        label: "Remaining income-tax balance due",
        field: "totalRemainingBalanceDue",
        auditCollections: ["liabilities", "credits", "payments"],
        formula: "sum of each liability after allocated foreign-tax credit and matching tax payment, floored at zero",
        exclusions: ["Property taxes, tax overpayments, and non-tax costs."]
      }
    ];
    return {
      id: "global_reconciliation",
      label: "Global liability, payment, and credit reconciliation",
      lines: scenarios.flatMap(function (scenario, index) {
        return definitions.map(function (definition) {
          const auditItems = definition.auditCollections.flatMap(function (key) { return scenario.globalReconciliation[key] || []; });
          const ruleIds = unique(auditItems.flatMap(function (item) { return item.ruleIds || []; }));
          const sourceIds = unique(auditItems.flatMap(function (item) { return item.sourceIds || []; }));
          return auditLine(Object.assign({}, shared, {
            key: definition.key + "_scenario_" + index,
            label: definition.label + " — " + scenario.id,
            value: scenario.globalReconciliation[definition.field],
            formula: definition.formula,
            assumptions: ["This line belongs only to the complete aligned scenario " + scenario.id + "."],
            exclusions: definition.exclusions,
            branchIds: [scenario.id],
            ruleIds: ruleIds.length ? ruleIds : ["no-applicable-global-allocation-rule"],
            sourceIds: sourceIds.length ? sourceIds : ["calculation-derived"]
          }));
        });
      })
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
        lines: propertyLines(jurisdiction.property, label, result)
      }
    ];
  }

  function explainCalculation(result) {
    if (!record(result) || !record(result.totals) || !record(result.retirementIntegration)) {
      throw new TypeError("DetailedTaxResult is required");
    }
    return jurisdictionSections(result, "destination", "Destination")
      .concat(jurisdictionSections(result, "continuingHome", "Continuing home"))
      .concat([reconciliationSection(result), totalsSection(result), retirementSection(result)]);
  }

  return { explainCalculation: explainCalculation };
});
