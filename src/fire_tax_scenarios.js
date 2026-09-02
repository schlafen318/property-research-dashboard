(function (root, factory) {
  const statutory = typeof module === "object" && module.exports
    ? require("./fire_tax_statutory.js")
    : root && root.GHAFireTaxStatutory;
  const api = factory(statutory);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxScenarios = api;
})(typeof window !== "undefined" ? window : null, function (statutory) {
  "use strict";

  function audit(rule, row, status) {
    const gain = rule.capital_gains || {};
    const formula = gain.base === "proceeds"
      ? "Current securities-transfer rate applied to the calculated portfolio withdrawal."
      : gain.base === "combined_assessable_income"
        ? "Incremental destination tax after adding the estimated realized gain above dependable income."
        : "Current destination rate or tax bands applied to the estimated realized gain.";
    return {
      status: status || "included",
      label: "destination capital-gains tax",
      formula: formula,
      assumptions: [
        "Calculated annual portfolio withdrawal: " + Math.round(row.portfolioWithdrawal).toLocaleString("en-US"),
        "Realized-gain share: " + Math.round(row.gainShare * 100) + "%",
        "Estimated realized gain: " + Math.round(row.realizedGain).toLocaleString("en-US"),
        "Full-year destination tax resident",
      ],
      inclusions: ["destination-side capital-gains tax on personal taxable listed securities"],
      exclusions: [
        "home-country tax and treaty interaction",
        "tax on pensions and other income",
        "account-specific exemptions, losses, deductions and filing costs",
      ],
      taxYear: String(rule.tax_year),
      confidence: "official source checked " + String(rule.checked_on),
      sourceIds: (rule.source_ids || []).slice(),
    };
  }

  function emptyCase(total) {
    return {
      total: total,
      incomeTaxReserve: total,
      propertyTaxReserve: 0,
      wealthTaxReserve: 0,
      complianceReserve: 0,
    };
  }

  function unavailable(reason) {
    return {
      status: "unavailable",
      conditional: true,
      planningBase: null,
      cases: {},
      amountExplanations: {},
      explanations: [{ category: "capital_gains_tax", status: "unavailable", reason: reason, sourceIds: [] }],
      sourceIds: [],
    };
  }

  function userAfterTax() {
    const row = emptyCase(0);
    const explanation = {
      status: "excluded",
      label: "destination tax reserve",
      formula: "0; user supplied after-tax assumptions",
      assumptions: ["taxMode=user_after_tax", "returnBasis=after_fees_and_tax"],
      inclusions: ["user-supplied after-tax assumptions"],
      exclusions: ["destination tax calculation"],
      taxYear: "not_applicable",
      confidence: "user_supplied",
      sourceIds: [],
    };
    return {
      status: "user_after_tax",
      conditional: false,
      planningBase: 0,
      cases: { user_after_tax: row },
      amountExplanations: { user_after_tax: { total: explanation } },
      explanations: [{ category: "user_after_tax", status: "excluded", reason: "User supplied after-tax inputs.", sourceIds: [] }],
      sourceIds: [],
    };
  }

  function estimateTaxScenario(input, countryRecord) {
    const profile = input || {};
    if (String(profile.taxMode || "destination_estimate") === "user_after_tax") return userAfterTax();
    if (!statutory || typeof statutory.estimateStatutoryTaxRange !== "function") {
      return unavailable("The statutory capital-gains engine is unavailable.");
    }
    const rule = countryRecord && countryRecord.statutory_screening;
    const result = statutory.estimateStatutoryTaxRange(profile, rule);
    if (result.status !== "available") {
      return unavailable(result.explanations && result.explanations[0]
        ? result.explanations[0].reason
        : "A current statutory capital-gains rule is unavailable.");
    }
    const keys = ["favorable", "central", "adverse"];
    const cases = {};
    const amountExplanations = {};
    result.cases.forEach(function (row, index) {
      const key = keys[index];
      cases[key] = Object.assign(emptyCase(row.capitalGainsTax), row);
      amountExplanations[key] = { total: audit(rule, row) };
    });
    return {
      status: "available",
      conditional: false,
      statutory: true,
      taxYear: String(result.taxYear),
      planningBase: result.cases[1].portfolioWithdrawal,
      estimate: result.estimate,
      minimum: result.minimum,
      maximum: result.maximum,
      cases: cases,
      amountExplanations: amountExplanations,
      explanations: result.explanations,
      sourceIds: result.sourceIds,
      assumptions: result.assumptions,
    };
  }

  return { estimateTaxScenario: estimateTaxScenario };
});
