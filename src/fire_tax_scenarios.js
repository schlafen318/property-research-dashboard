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
    CASES.forEach(function (key) {
      cases[key] = {
        total: null,
        incomeTaxReserve: null,
        propertyTaxReserve: null,
        wealthTaxReserve: null,
        complianceReserve: null,
      };
    });
    return {
      status: "unavailable",
      conditional: true,
      planningBase: null,
      cases: cases,
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
    if (!asOf) return false;
    const reviewed = parseIsoDate(screen.last_reviewed);
    const current = parseIsoDate(asOf);
    if (reviewed === null || current === null) return true;
    return current - reviewed > 366 * 24 * 60 * 60 * 1000;
  }

  function estimateTaxScenario(rawInput, countryRecord) {
    const input = rawInput || {};
    const taxMode = selected(input.taxMode, new Set(["destination_estimate", "user_after_tax"]), "destination_estimate", "taxMode");
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
    if (taxMode === "user_after_tax") {
      return {
        status: "user_after_tax",
        conditional: false,
        planningBase: 0,
        cases: cases,
        explanations: [{
          category: "user_after_tax",
          status: "excluded",
          reason: "User supplied after-tax inputs, so no destination tax scenario is added.",
          sourceIds: [],
        }],
        sourceIds: [],
      };
    }

    const screen = countryRecord && countryRecord.tax_screen || {};
    if (screen.status !== "complete") {
      return unavailable("Tax scenario evidence is not complete for this destination.");
    }
    if (staleEvidence(screen, input.asOf)) {
      return unavailable("Tax scenario evidence is stale for this destination.");
    }
    if (!screen.planning_bands || !screen.gain_intensity_modifiers || !screen.annual_allowances) {
      return unavailable("Tax scenario assumptions are missing for this destination.");
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
    CASES.forEach(function (key) {
      const rate = number(band[key + "_rate"], key + " planning rate");
      cases[key].incomeTaxReserve = Math.round(planningBase * rate * modifier);
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
          sourceIds: allowance.source_ids || [],
        });
        return;
      }
      if (!allowanceApplies(allowance, normalized, category)) {
        explanations.push({
          category: category,
          status: "not_applicable",
          reason: "The selected profile does not trigger this allowance.",
          sourceIds: allowance.source_ids || [],
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
      });
    });

    CASES.forEach(function (key) {
      cases[key].total = cases[key].incomeTaxReserve +
        cases[key].propertyTaxReserve +
        cases[key].wealthTaxReserve +
        cases[key].complianceReserve;
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
      explanations: explanations,
      sourceIds: sourceIds,
    };
  }

  return {
    estimateTaxScenario: estimateTaxScenario,
  };
});
