(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.GHAFireTaxStatutory = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const DAY_MS = 24 * 60 * 60 * 1000;

  function finiteNonNegative(value, label) {
    const number = Number(value || 0);
    if (!Number.isFinite(number) || number < 0) throw new Error(label + " must be non-negative");
    return number;
  }

  function unavailable(reason) {
    return { status: "unavailable", conditional: true, explanations: [{ reason: reason }] };
  }

  function isStale(rule, asOf) {
    const checked = Date.parse(String(rule && rule.checked_on || ""));
    const anchor = Date.parse(String(asOf || ""));
    const interval = Number(rule && rule.review_interval_days);
    return !Number.isFinite(checked) || !Number.isFinite(anchor) ||
      !Number.isInteger(interval) || interval <= 0 || anchor < checked ||
      (anchor - checked) / DAY_MS > interval;
  }

  function progressiveTax(amount, bands) {
    let remaining = Math.max(0, Number(amount));
    let lower = 0;
    let total = 0;
    (bands || []).forEach(function (band) {
      if (remaining <= 0) return;
      const upper = band.up_to === null ? Infinity : Number(band.up_to);
      const width = upper === Infinity ? remaining : Math.max(0, upper - lower);
      const taxable = Math.min(remaining, width);
      total += taxable * Number(band.rate);
      remaining -= taxable;
      lower = upper;
    });
    return total;
  }

  function caseTax(input, rule, gainShare) {
    const withdrawalUsd = finiteNonNegative(input.portfolioWithdrawals, "portfolioWithdrawals");
    const dependableIncomeUsd = finiteNonNegative(input.dependableIncome, "dependableIncome");
    const fxToUsd = Number(input.fxToUsd);
    if (!Number.isFinite(fxToUsd) || fxToUsd <= 0) throw new Error("fxToUsd must be positive");
    const gainUsd = withdrawalUsd * gainShare;
    const gain = rule.capital_gains;
    let baseUsd = gainUsd;
    if (gain.base === "proceeds") baseUsd = withdrawalUsd;
    if (gain.base === "combined_assessable_income") baseUsd = dependableIncomeUsd + gainUsd;
    if (gain.base === "remitted_gain") {
      baseUsd = gain.remittance_assumption === "not_remitted" ? 0 : gainUsd;
    }
    const baseLocal = baseUsd / fxToUsd;
    let taxLocal = 0;
    let reason = "Current statutory capital-gains rule applied to the modeled taxable base.";
    if (gain.calculation === "flat_rate" || gain.calculation === "proceeds_rate" ||
        gain.calculation === "conditional_exemption") {
      taxLocal = baseLocal * Number(gain.rate);
    } else if (gain.calculation === "holding_period_exemption") {
      if (Number(gain.holding_period_assumption_years) >= Number(gain.exemption_after_years)) {
        reason = "The disclosed holding-period exemption applies to this screening assumption.";
      } else {
        taxLocal = baseLocal * Number(gain.rate);
        reason = "The screening assumption does not claim the statutory holding-period exemption.";
      }
    } else if (gain.calculation === "progressive_rate" ||
               gain.calculation === "remittance_progressive_rate") {
      taxLocal = progressiveTax(baseLocal, gain.bands);
      if (gain.base === "combined_assessable_income") {
        taxLocal -= progressiveTax(dependableIncomeUsd / fxToUsd, gain.bands);
        reason = "Incremental tax from the modeled gain after stacking it above dependable income.";
      }
    } else {
      throw new Error("Unsupported statutory calculation");
    }
    return {
      gainShare: gainShare,
      portfolioWithdrawal: Math.round(withdrawalUsd),
      realizedGain: Math.round(gainUsd),
      statutoryBase: Math.round(baseUsd),
      capitalGainsTax: Math.round(taxLocal * fxToUsd),
      totalAnnualTax: Math.round(taxLocal * fxToUsd),
      reason: reason,
    };
  }

  function estimateStatutoryTaxRange(input, rule) {
    if (!rule || typeof rule !== "object" || !rule.capital_gains) {
      return unavailable("A complete statutory destination rule is unavailable.");
    }
    if (isStale(rule, input && input.asOf)) {
      return unavailable("The statutory destination rule is stale or lacks a valid freshness anchor.");
    }
    try {
      const gainShares = Array.isArray(input.gainShares) ? input.gainShares : [0, 0.5, 1];
      if (gainShares.length !== 3 || gainShares[0] !== 0 || gainShares[1] !== 0.5 || gainShares[2] !== 1) {
        throw new Error("gainShares must equal 0, 0.5, and 1");
      }
      const cases = gainShares.map(function (share) { return caseTax(input, rule, share); });
      const totals = cases.map(function (row) { return row.totalAnnualTax; });
      const estimateCase = cases[1];
      return {
        status: "available",
        taxYear: rule.tax_year,
        country: rule.country,
        estimate: estimateCase.totalAnnualTax,
        minimum: Math.min.apply(Math, totals),
        maximum: Math.max.apply(Math, totals),
        cases: cases,
        sourceIds: (rule.source_ids || []).slice(),
        assumptions: {
          residence: rule.residence_assumption,
          portfolioScope: rule.portfolio_scope,
          gainShares: gainShares.slice(),
        },
        explanations: [{
          reason: cases[1].reason,
          destinationSideOnly: true,
          sourceIds: (rule.source_ids || []).slice(),
        }],
      };
    } catch (error) {
      return unavailable(error instanceof Error ? error.message : "The statutory calculation failed.");
    }
  }

  return {
    estimateStatutoryTaxRange: estimateStatutoryTaxRange,
    progressiveTax: progressiveTax,
  };
});
