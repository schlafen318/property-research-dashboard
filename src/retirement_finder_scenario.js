(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementFinderScenario = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const MAX_ENCODED_LENGTH = 16384;
  const MAX_RESULTS = 100;
  const TIERS = new Set(["within_reach", "close", "stretch"]);
  const HOUSEHOLDS = new Set(["single", "couple"]);
  const HOUSING_PLANS = new Set(["rent", "own", "buy_now", "buy_retirement"]);
  const HEALTHCARE = new Set(["normal", "high"]);

  function finite(value, label) {
    if (value === null || value === "" || typeof value === "boolean") {
      throw new Error(label + " must be finite");
    }
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) throw new Error(label + " must be finite");
    return parsed;
  }

  function nonNegative(value, label) {
    const parsed = finite(value, label);
    if (parsed < 0) throw new Error(label + " must be non-negative");
    return parsed;
  }

  function shortString(value, label, allowEmpty) {
    const result = String(value == null ? "" : value).trim();
    if ((!allowEmpty && !result) || result.length > 100) throw new Error(label + " is invalid");
    return result;
  }

  function enumValue(value, allowed, label) {
    const result = String(value || "");
    if (!allowed.has(result)) throw new Error(label + " is invalid");
    return result;
  }

  function publicResult(item) {
    return {
      destinationId: item.destinationId,
      retirementTargetUsd: item.retirementTargetUsd != null ? item.retirementTargetUsd : item.retirementTarget,
      surplusGapUsd: item.surplusGapUsd != null ? item.surplusGapUsd : item.surplusGap,
      fundingRatio: item.fundingRatio,
      tier: item.tier,
      preferenceMatches: Array.isArray(item.preferenceMatches) ? item.preferenceMatches.slice() : [],
    };
  }

  function normalizedDestinationIds(destinationIds) {
    if (destinationIds instanceof Set) return destinationIds;
    if (!Array.isArray(destinationIds)) throw new Error("Destination IDs are required");
    return new Set(destinationIds.map(String));
  }

  function validateScenario(input, destinationIds, options) {
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      throw new Error("Results link is invalid");
    }
    if (Number(input.v) !== 1) throw new Error("Unsupported results-link version");

    const knownDestinations = normalizedDestinationIds(destinationIds);
    const allowMissingDestinations = Boolean(options && options.allowMissingDestinations);
    const currency = shortString(input.currency, "Currency", false).toUpperCase();
    if (!/^[A-Z]{3}$/.test(currency)) throw new Error("Currency is invalid");
    const household = enumValue(input.household, HOUSEHOLDS, "Household");
    const housingPlan = enumValue(input.housingPlan, HOUSING_PLANS, "Housing plan");
    const horizonYears = nonNegative(input.horizonYears, "Retirement horizon");
    if (horizonYears <= 0 || horizonYears > 100) throw new Error("Retirement horizon is invalid");

    const preferences = input.preferences || {};
    const normalizedPreferences = {
      region: shortString(preferences.region || "any", "Region", false),
      climate: shortString(preferences.climate || "any", "Setting", false),
      healthcare: enumValue(preferences.healthcare || "normal", HEALTHCARE, "Healthcare preference"),
    };

    if (!Array.isArray(input.results) || input.results.length > MAX_RESULTS) {
      throw new Error("Results list is invalid");
    }
    const seen = new Set();
    const sourceSeen = new Set();
    const results = input.results.map(function (item) {
      if (!item || typeof item !== "object" || Array.isArray(item)) throw new Error("Destination result is invalid");
      const destinationId = shortString(item.destinationId, "Destination ID", false);
      if (sourceSeen.has(destinationId)) throw new Error("Destination IDs must be unique");
      sourceSeen.add(destinationId);
      if (!knownDestinations.has(destinationId)) {
        if (allowMissingDestinations) return null;
        throw new Error("Unknown destination: " + destinationId);
      }
      seen.add(destinationId);
      const preferenceMatches = Array.isArray(item.preferenceMatches) ? item.preferenceMatches : [];
      if (preferenceMatches.length > 4) throw new Error("Preference matches are invalid");
      return {
        destinationId: destinationId,
        retirementTargetUsd: nonNegative(item.retirementTargetUsd, "Required capital"),
        surplusGapUsd: finite(item.surplusGapUsd, "Capital gap"),
        fundingRatio: nonNegative(item.fundingRatio, "Funding ratio"),
        tier: enumValue(item.tier, TIERS, "Financial tier"),
        preferenceMatches: preferenceMatches.map(function (match) {
          return shortString(match, "Preference match", false);
        }),
      };
    }).filter(Boolean);

    if (!Array.isArray(input.comparisonIds)) throw new Error("Comparison destinations are required");
    const expectedComparisonCount = Math.min(3, results.length);
    if (!allowMissingDestinations && input.comparisonIds.length !== expectedComparisonCount) {
      throw new Error("Comparison destinations are invalid");
    }
    const comparisonSeen = new Set();
    let comparisonIds = input.comparisonIds.map(function (value) {
      const destinationId = shortString(value, "Comparison destination", false);
      if (!seen.has(destinationId)) {
        if (allowMissingDestinations) return null;
        throw new Error("Unknown comparison destination: " + destinationId);
      }
      if (comparisonSeen.has(destinationId)) throw new Error("Comparison destination IDs must be unique");
      comparisonSeen.add(destinationId);
      return destinationId;
    }).filter(Boolean);
    if (allowMissingDestinations) {
      results.forEach(function (item) {
        if (comparisonIds.length < expectedComparisonCount && !comparisonSeen.has(item.destinationId)) {
          comparisonSeen.add(item.destinationId);
          comparisonIds.push(item.destinationId);
        }
      });
    }

    const dataReviewed = shortString(input.dataReviewed, "Data review date", false);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dataReviewed)) throw new Error("Data review date is invalid");
    const dateParts = dataReviewed.split("-").map(Number);
    const reviewedDate = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
    if (reviewedDate.getUTCFullYear() !== dateParts[0] || reviewedDate.getUTCMonth() !== dateParts[1] - 1 || reviewedDate.getUTCDate() !== dateParts[2]) {
      throw new Error("Data review date is invalid");
    }

    return {
      v: 1,
      currency: currency,
      projectedCapitalUsd: nonNegative(input.projectedCapitalUsd, "Projected capital"),
      household: household,
      horizonYears: horizonYears,
      housingPlan: housingPlan,
      preferences: normalizedPreferences,
      results: results,
      comparisonIds: comparisonIds,
      dataReviewed: dataReviewed,
    };
  }

  function buildScenario(input) {
    const result = input && input.result || {};
    const user = input && input.user || {};
    const recommendations = Array.isArray(result.recommendations) ? result.recommendations : [];
    const scenario = {
      v: 1,
      currency: input && input.currency || "USD",
      projectedCapitalUsd: input && input.projectedCapitalUsd,
      household: user.household,
      horizonYears: user.horizonYears,
      housingPlan: user.housingPlan,
      preferences: user.preferences || {},
      results: recommendations.map(publicResult),
      comparisonIds: recommendations.slice(0, 3).map(function (item) { return item.destinationId; }),
      dataReviewed: input && input.dataReviewed,
    };
    return validateScenario(scenario, recommendations.map(function (item) { return item.destinationId; }));
  }

  function utf8ToBase64(value) {
    if (typeof Buffer !== "undefined") return Buffer.from(value, "utf8").toString("base64");
    const bytes = new TextEncoder().encode(value);
    let binary = "";
    bytes.forEach(function (byte) { binary += String.fromCharCode(byte); });
    return btoa(binary);
  }

  function base64ToUtf8(value) {
    if (typeof Buffer !== "undefined") return Buffer.from(value, "base64").toString("utf8");
    const binary = atob(value);
    const bytes = Uint8Array.from(binary, function (character) { return character.charCodeAt(0); });
    return new TextDecoder().decode(bytes);
  }

  function encodeScenario(scenario) {
    const knownIds = Array.isArray(scenario && scenario.results)
      ? scenario.results.map(function (item) { return item.destinationId; })
      : [];
    const validated = validateScenario(scenario, knownIds);
    const encoded = utf8ToBase64(JSON.stringify(validated))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");
    if (encoded.length > MAX_ENCODED_LENGTH) throw new Error("Results link is too large");
    return encoded;
  }

  function decodeScenario(value, destinationIds) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      destinationIds = value.destinationIds;
      value = value.value;
    }
    const encoded = String(value || "");
    if (!encoded || encoded.length > MAX_ENCODED_LENGTH) throw new Error("Results link is too large");
    if (!/^[A-Za-z0-9_-]+$/.test(encoded)) throw new Error("Results link is invalid");
    let parsed;
    try {
      const padded = encoded.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - encoded.length % 4) % 4);
      parsed = JSON.parse(base64ToUtf8(padded));
    } catch (error) {
      throw new Error("Results link is invalid");
    }
    return validateScenario(parsed, destinationIds, { allowMissingDestinations: true });
  }

  return {
    buildScenario: buildScenario,
    validateScenario: validateScenario,
    encodeScenario: encodeScenario,
    decodeScenario: decodeScenario,
  };
});
