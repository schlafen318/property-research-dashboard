(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxScenarios = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const CASES = ["favorable", "central", "adverse"];
  const VALID_STAY_MODES = new Set(["seasonal", "part_year", "full_relocation"]);
  const VALID_GAIN_INTENSITIES = new Set(["low", "moderate", "high"]);
  const VALID_PROPERTY_USES = new Set(["none", "personal", "rental", "mixed"]);
  const VALID_WEALTH_BANDS = new Set(["under_threshold", "above_threshold", "unknown"]);
  const REQUIRED_ALLOWANCES = ["property_tax", "wealth_tax", "compliance"];

  function number(value, label) {
    const result = Number(value);
    if (!Number.isFinite(result) || result < 0) {
      throw new Error(label + " must be a finite non-negative number");
    }
    return result;
  }

  function selected(value, allowed, fallback, label) {
    const result = value === undefined || value === null || value === "" ? fallback : String(value);
    if (!allowed.has(result)) throw new Error(label + " is invalid");
    return result;
  }

  function unavailable(reason) {
    const cases = {};
    const amountExplanations = {};
    CASES.forEach(function (key) {
      cases[key] = {
        total: null,
        incomeTaxReserve: null,
        propertyTaxReserve: null,
        wealthTaxReserve: null,
        complianceReserve: null,
      };
      amountExplanations[key] = {};
    });
    return {
      status: "unavailable",
      conditional: true,
      planningBase: null,
      cases: cases,
      amountExplanations: amountExplanations,
      explanations: [{ category: "scenario_evidence", status: "unavailable", reason: reason, sourceIds: [] }],
      sourceIds: [],
    };
  }

  function allowanceApplies(allowance, input, category) {
    if (category === "property_tax") {
      const uses = allowance.applies_to_property_uses || [];
      return uses.indexOf(input.propertyUse) !== -1;
    }
    if (category === "wealth_tax") {
      const bands = allowance.applies_to_wealth_bands || [];
      return bands.indexOf(input.wealthBand) !== -1;
    }
    return true;
  }

  function allowanceAmount(allowance, key) {
    return Math.round(number(allowance[key + "_usd"], key + " allowance"));
  }

  function unique(values) {
    const seen = new Set();
    const result = [];
    values.forEach(function (value) {
      if (!value || seen.has(value)) return;
      seen.add(value);
      result.push(value);
    });
    return result;
  }

  function parseIsoDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(value || ""))) return null;
    const parts = String(value).split("-").map(Number);
    return Date.UTC(parts[0], parts[1] - 1, parts[2]);
  }

  function staleEvidence(screen, asOf) {
    const reviewed = parseIsoDate(screen.last_reviewed);
    const current = parseIsoDate(asOf);
    if (reviewed === null || current === null) return true;
    return current - reviewed > 366 * 24 * 60 * 60 * 1000;
  }

  function completeAllowance(allowance) {
    return allowance &&
      Array.isArray(allowance.source_ids) &&
      allowance.source_ids.length > 0 &&
      CASES.every(function (key) {
        const amount = Number(allowance[key + "_usd"]);
        return Number.isFinite(amount) && amount >= 0;
      });
  }

  function completeAllowances(screen) {
    const allowances = screen.annual_allowances;
    if (!allowances) return false;
    return REQUIRED_ALLOWANCES.every(function (key) {
      return completeAllowance(allowances[key]);
    });
  }

  function amountExplanation(input) {
    return {
      status: input.status || "included",
      label: input.label,
      formula: input.formula,
      assumptions: input.assumptions,
      inclusions: input.inclusions,
      exclusions: input.exclusions,
      taxYear: input.taxYear,
      confidence: input.confidence,
      sourceIds: input.sourceIds || [],
    };
  }

  function estimateTaxScenario(rawInput, countryRecord) {
    const input = rawInput || {};
    const taxMode = selected(input.taxMode, new Set(["destination_estimate", "user_after_tax"]), "destination_estimate", "taxMode");
    if (taxMode === "user_after_tax") {
      const zeroCase = {
        total: 0,
        incomeTaxReserve: 0,
        propertyTaxReserve: 0,
        wealthTaxReserve: 0,
        complianceReserve: 0,
      };
      const excludedLabels = {
        total: "destination tax scenario",
        incomeTaxReserve: "destination income tax reserve",
        propertyTaxReserve: "destination property tax reserve",
        wealthTaxReserve: "destination wealth tax reserve",
        complianceReserve: "destination compliance reserve",
      };
      const afterTaxExplanations = {};
      Object.keys(zeroCase).forEach(function (field) {
        afterTaxExplanations[field] = amountExplanation({
          status: "excluded",
          label: field === "total" ? "tax reserve" : excludedLabels[field],
          formula: "0; user supplied after-tax assumptions",
          assumptions: ["taxMode=user_after_tax", "returnBasis=after_fees_and_tax"],
          inclusions: ["user-supplied after-tax income and portfolio return assumptions"],
          exclusions: [excludedLabels[field]],
          taxYear: "not_applicable",
          confidence: "user_supplied",
          sourceIds: [],
        });
      });
      return {
        status: "user_after_tax",
        conditional: false,
        planningBase: 0,
        cases: { user_after_tax: zeroCase },
        amountExplanations: { user_after_tax: afterTaxExplanations },
        explanations: [{
          category: "user_after_tax",
          status: "excluded",
          reason: "User supplied after-tax inputs, so no destination tax scenario is added.",
          sourceIds: [],
        }],
        sourceIds: [],
      };
    }
    const cases = {};
    CASES.forEach(function (key) {
      cases[key] = {
        total: 0,
        incomeTaxReserve: 0,
        propertyTaxReserve: 0,
        wealthTaxReserve: 0,
        complianceReserve: 0,
      };
    });
    const screen = countryRecord && countryRecord.tax_screen || {};
    if (screen.status !== "complete") {
      return unavailable("Tax scenario evidence is not complete for this destination.");
    }
    const asOf = input.asOf || countryRecord.as_of || countryRecord.reviewed_on;
    if (!asOf) {
      return unavailable("A freshness anchor is required for destination tax scenarios.");
    }
    if (staleEvidence(screen, asOf)) {
      return unavailable("Tax scenario evidence is stale for this destination.");
    }
    if (!screen.planning_bands || !screen.gain_intensity_modifiers || !completeAllowances(screen)) {
      return unavailable("Tax scenario allowance assumptions are missing for this destination.");
    }

    const stayMode = selected(input.stayMode, VALID_STAY_MODES, "part_year", "stayMode");
    const realizedGainIntensity = selected(
      input.realizedGainIntensity,
      VALID_GAIN_INTENSITIES,
      "moderate",
      "realizedGainIntensity"
    );
    const propertyUse = selected(input.propertyUse, VALID_PROPERTY_USES, "none", "propertyUse");
    const wealthBand = selected(input.wealthBand, VALID_WEALTH_BANDS, "unknown", "wealthBand");
    const normalized = {
      propertyUse: propertyUse,
      wealthBand: wealthBand,
    };
    const planningBase = number(input.dependableIncome, "dependableIncome") +
      number(input.portfolioWithdrawals, "portfolioWithdrawals");
    const band = screen.planning_bands[stayMode];
    const modifier = Number(screen.gain_intensity_modifiers[realizedGainIntensity]);
    if (!band || !Number.isFinite(modifier) || modifier < 0) {
      return unavailable("Tax scenario assumptions are incomplete for the selected profile.");
    }

    const explanations = [{
      category: "income_tax",
      status: "included",
      reason: "Planning reserve uses the selected stay mode and realized-gain intensity.",
      sourceIds: unique([].concat(screen.planning_band_basis_source_ids || [], screen.gain_intensity_source_ids || [])),
    }];
    const taxYear = String(input.taxYear || screen.last_reviewed).slice(0, 4);
    const confidence = screen.confidence || "low";
    const amountExplanations = {};
    CASES.forEach(function (key) {
      const rate = number(band[key + "_rate"], key + " planning rate");
      cases[key].incomeTaxReserve = Math.round(planningBase * rate * modifier);
      amountExplanations[key] = {
        incomeTaxReserve: amountExplanation({
          status: "included",
          label: "income tax reserve",
          formula: "round((dependableIncome + portfolioWithdrawals) * " + key + "_rate * gain_intensity_modifier)",
          assumptions: [
            "dependableIncome=" + number(input.dependableIncome, "dependableIncome"),
            "portfolioWithdrawals=" + number(input.portfolioWithdrawals, "portfolioWithdrawals"),
            "stayMode=" + stayMode,
            "realizedGainIntensity=" + realizedGainIntensity,
          ],
          inclusions: ["dependable income", "portfolio withdrawals"],
          exclusions: ["statutory tax calculation", "home-country tax interaction"],
          taxYear: taxYear,
          confidence: confidence,
          sourceIds: unique([].concat(screen.planning_band_basis_source_ids || [], screen.gain_intensity_source_ids || [])),
        }),
      };
    });

    const allowances = screen.annual_allowances || {};
    [
      ["property_tax", "propertyTaxReserve"],
      ["wealth_tax", "wealthTaxReserve"],
      ["compliance", "complianceReserve"],
    ].forEach(function (entry) {
      const category = entry[0];
      const field = entry[1];
      const allowance = allowances[category];
      if (!allowance) return;
      if (category === "property_tax" && input.propertyTaxIncludedInRetirementCosts) {
        explanations.push({
          category: category,
          status: "excluded",
          reason: "Annual property tax is already included in owner retirement costs.",
          sourceIds: [],
        });
        CASES.forEach(function (key) {
          amountExplanations[key][field] = amountExplanation({
            status: "excluded",
            label: allowance.label || category,
            formula: "0; excluded because owner retirement costs already include annual property tax",
            assumptions: ["propertyTaxIncludedInRetirementCosts=true"],
            inclusions: ["evaluated annual property ownership tax allowance"],
            exclusions: ["annual property tax already in owner retirement costs"],
            taxYear: taxYear,
            confidence: confidence,
            sourceIds: [],
          });
        });
        return;
      }
      if (!allowanceApplies(allowance, normalized, category)) {
        explanations.push({
          category: category,
          status: "not_applicable",
          reason: "The selected profile does not trigger this allowance.",
          sourceIds: [],
        });
        CASES.forEach(function (key) {
          amountExplanations[key][field] = amountExplanation({
            status: "not_applicable",
            label: allowance.label || category,
            formula: "0; selected profile does not trigger this allowance",
            assumptions: ["propertyUse=" + propertyUse, "wealthBand=" + wealthBand],
            inclusions: ["evaluated " + (allowance.label || category)],
            exclusions: [allowance.label || category],
            taxYear: taxYear,
            confidence: confidence,
            sourceIds: [],
          });
        });
        return;
      }
      explanations.push({
        category: category,
        status: "included",
        reason: allowance.label || category,
        sourceIds: allowance.source_ids || [],
      });
      CASES.forEach(function (key) {
        cases[key][field] = allowanceAmount(allowance, key);
        amountExplanations[key][field] = amountExplanation({
          status: "included",
          label: allowance.label || category,
          formula: key + "_usd from annual_allowances." + category,
          assumptions: ["propertyUse=" + propertyUse, "wealthBand=" + wealthBand],
          inclusions: [allowance.label || category],
          exclusions: ["buyer-specific statutory calculation"],
          taxYear: taxYear,
          confidence: confidence,
          sourceIds: allowance.source_ids || [],
        });
      });
    });

    CASES.forEach(function (key) {
      cases[key].total = cases[key].incomeTaxReserve +
        cases[key].propertyTaxReserve +
        cases[key].wealthTaxReserve +
        cases[key].complianceReserve;
      const componentFields = [
        "incomeTaxReserve",
        "propertyTaxReserve",
        "wealthTaxReserve",
        "complianceReserve",
      ];
      const active = componentFields.map(function (field) {
        return amountExplanations[key][field];
      }).filter(function (explanation) {
        return explanation.status === "included";
      });
      const inactive = componentFields.map(function (field) {
        return amountExplanations[key][field];
      }).filter(function (explanation) {
        return explanation.status !== "included";
      });
      amountExplanations[key].total = amountExplanation({
        status: "included",
        label: "tax reserve",
        formula: "incomeTaxReserve + propertyTaxReserve + wealthTaxReserve + complianceReserve",
        assumptions: ["taxMode=destination_estimate", "taxYear=" + taxYear],
        inclusions: active.map(function (explanation) { return explanation.label; }),
        exclusions: inactive.map(function (explanation) {
          return explanation.label + (explanation.status === "not_applicable"
            ? " (not applicable)"
            : " (excluded: already included in retirement costs)");
        }).concat(["transaction taxes", "sale taxes", "succession taxes"]),
        taxYear: taxYear,
        confidence: confidence,
        sourceIds: unique(active.reduce(function (all, explanation) {
          return all.concat(explanation.sourceIds || []);
        }, [])),
      });
    });

    const sourceIds = unique(explanations.reduce(function (all, item) {
      if (item.status !== "included") return all;
      return all.concat(item.sourceIds || []);
    }, []));
    return {
      status: "available",
      conditional: false,
      planningBase: Math.round(planningBase),
      cases: cases,
      amountExplanations: amountExplanations,
      explanations: explanations,
      sourceIds: sourceIds,
    };
  }

  return {
    estimateTaxScenario: estimateTaxScenario,
  };
});
