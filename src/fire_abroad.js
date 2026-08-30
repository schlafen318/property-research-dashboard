(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.GHAFireAbroad = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const FIRE_WEIGHTS = {
    active_life: 0.25,
    sustainable_annual_cost: 0.20,
    healthcare_bridge: 0.15,
    stay_flexibility: 0.10,
    tax_compatibility: 0.10,
    global_access: 0.08,
    community_fit: 0.07,
    property_exit_flexibility: 0.05,
  };
  const ACTIVE_LIFE_WEIGHTS = {
    everyday_movement: 0.30,
    active_pursuits: 0.30,
    year_round_continuity: 0.25,
    activity_ecosystem: 0.15,
  };
  const PROFILE_DEFAULTS = {
    stay_mode: "part_year",
    age: 50,
    household: "single",
    housing: "rent",
    mobility_rights: "prefer_not_to_say",
    home_tax_context: "prefer_not_to_say",
    annual_days: null,
    income_type: "prefer_not_to_say",
    activity_priority: "balanced",
  };
  const PROFILE_ALLOWLISTS = {
    stay_mode: new Set(["seasonal", "part_year", "full_relocation"]),
    household: new Set(["single", "couple"]),
    housing: new Set(["rent", "own", "buy_now", "buy_retirement"]),
    mobility_rights: new Set(["local_free_movement", "general_nonlocal", "prefer_not_to_say"]),
    home_tax_context: new Set(["us_person", "other", "prefer_not_to_say"]),
    income_type: new Set(["portfolio", "pension", "property", "business_consulting", "mixed", "prefer_not_to_say"]),
    activity_priority: new Set(["balanced", "walking", "cycling", "hiking", "water", "winter_sports", "fitness_social"]),
  };
  const COST_SCORE_ANCHORS = {
    single: { five: 30000, zero: 90000 },
    couple: { five: 45000, zero: 135000 },
  };
  const UNRANKED_STATUSES = new Set(["needs_verification", "not_eligible"]);
  const VALID_ELIGIBILITY = new Set(["eligible", "conditional", "needs_verification", "not_eligible"]);
  const VALID_WORK_PERMISSIONS = new Set(["passive_only", "remote_permitted", "local_permitted", "unclear"]);

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function isNumber(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function round2(value) {
    return Number(value.toFixed(2));
  }

  function normalizeProfile(raw) {
    const input = isObject(raw) ? raw : {};
    const normalized = Object.assign({}, PROFILE_DEFAULTS);
    Object.keys(PROFILE_ALLOWLISTS).forEach(function (key) {
      if (typeof input[key] === "string" && PROFILE_ALLOWLISTS[key].has(input[key])) {
        normalized[key] = input[key];
      }
    });
    if (isNumber(input.age)) normalized.age = Math.max(18, Math.min(100, Math.trunc(input.age)));
    if (Number.isInteger(input.annual_days) && input.annual_days >= 1 && input.annual_days <= 366) {
      normalized.annual_days = input.annual_days;
    }
    return normalized;
  }

  function numericScore(value) {
    const candidate = isObject(value) ? value.score : value;
    return isNumber(candidate) && candidate >= 0 && candidate <= 5 ? candidate : null;
  }

  function activeLifeScore(record) {
    const activeLife = isObject(record) && Object.prototype.hasOwnProperty.call(record, "active_life")
      ? record.active_life : record;
    if (!isObject(activeLife)) return 0;
    let total = 0;
    for (const component of Object.keys(ACTIVE_LIFE_WEIGHTS)) {
      const score = numericScore(activeLife[component]);
      if (score === null) return 0;
      total += score * ACTIVE_LIFE_WEIGHTS[component];
    }
    return round2(total);
  }

  function eligibilityForMode(country, profile) {
    const normalized = normalizeProfile(profile);
    const routes = isObject(country) && isObject(country.stay_routes) ? country.stay_routes : {};
    const route = isObject(routes[normalized.stay_mode]) ? routes[normalized.stay_mode] : null;
    if (!route) {
      return {
        status: "needs_verification",
        reason: "No documented route is available for this stay mode.",
        work_permission: "unclear",
        stay_score: null,
      };
    }
    let status = route.status;
    const summary = typeof route.summary === "string" && route.summary ? route.summary : "Route conditions require confirmation.";
    const workPermission = VALID_WORK_PERMISSIONS.has(route.work_permission) ? route.work_permission : "unclear";
    if (isObject(route.mobility_rights)) {
      const selected = route.mobility_rights[normalized.mobility_rights];
      if (!VALID_ELIGIBILITY.has(selected)) {
        return {
          status: "needs_verification",
          reason: "Nationality-dependent mobility rights must be confirmed.",
          work_permission: workPermission,
          stay_score: null,
        };
      }
      status = selected;
    }
    if (Number.isInteger(route.minimum_age) && normalized.age < route.minimum_age) {
      return {
        status: "not_eligible",
        reason: "This route requires an age of at least " + route.minimum_age + ".",
        work_permission: workPermission,
        stay_score: 0,
      };
    }
    if (!VALID_ELIGIBILITY.has(status)) status = "needs_verification";
    let score = numericScore(route.base_score);
    if (UNRANKED_STATUSES.has(status) || score === null) score = null;
    else {
      if (normalized.income_type === "business_consulting") {
        if (workPermission === "passive_only") score -= 0.5;
        else if (workPermission === "unclear") score -= 1;
      }
      score = round2(Math.max(0, Math.min(5, score)));
    }
    return { status: status, reason: summary, work_permission: workPermission, stay_score: score };
  }

  function annualCostScore(annualTotalUsd, household) {
    const anchors = COST_SCORE_ANCHORS[household];
    const ratio = (annualTotalUsd - anchors.five) / (anchors.zero - anchors.five);
    return round2(Math.max(0, Math.min(5, 5 * (1 - ratio))));
  }

  function buildResilienceBudget(cost, profile, destinationOverride) {
    const normalized = normalizeProfile(profile);
    const source = isObject(cost) ? cost : {};
    const profiles = isObject(source.profiles) ? source.profiles : {};
    const householdCost = isObject(profiles[normalized.household]) ? profiles[normalized.household] : {};
    const rawCategories = isObject(householdCost.categories_usd) ? householdCost.categories_usd : {};
    const categories = {};
    Object.keys(rawCategories).forEach(function (key) {
      if (isNumber(rawCategories[key])) categories[key] = rawCategories[key];
    });
    const rents = normalized.housing === "rent" || normalized.housing === "buy_retirement";
    const housingCost = rents ? householdCost.annual_rent_usd : householdCost.annual_owner_costs_usd;
    if (isNumber(housingCost)) categories[rents ? "rent" : "owner_costs"] = housingCost;
    const property = isObject(source.property) ? source.property : {};
    let propertyCapital = 0;
    if (normalized.housing === "buy_now" || normalized.housing === "buy_retirement") {
      if (isNumber(property.representative_price_usd) && isNumber(property.acquisition_cost_rate)) {
        propertyCapital = round2(property.representative_price_usd * (1 + property.acquisition_cost_rate));
      }
    }
    const recurringWithoutContingency = Object.keys(categories).reduce(function (total, key) {
      return total + (key === "contingency" ? 0 : categories[key]);
    }, 0);
    const currencyInflationBuffer = Math.floor(recurringWithoutContingency * 0.10 + 0.5);
    const annualTotal = round2(Object.keys(categories).reduce(function (total, key) {
      return total + categories[key];
    }, 0) + currencyInflationBuffer);
    const override = isObject(destinationOverride) ? destinationOverride : {};
    const relocation = isNumber(override.one_time_relocation_usd) ? override.one_time_relocation_usd : 0;
    return {
      annual_total_usd: annualTotal,
      categories: categories,
      currency_inflation_buffer: currencyInflationBuffer,
      property_capital_usd: propertyCapital,
      one_time_relocation_usd: relocation,
    };
  }

  function destinationScore(destination, dimension) {
    if (!isObject(destination)) return null;
    if (Array.isArray(destination.decision_dimensions)) {
      for (const item of destination.decision_dimensions) {
        if (isObject(item) && item.key === dimension) return numericScore(item);
      }
    }
    const direct = numericScore(destination[dimension]);
    if (direct !== null) return direct;
    return isObject(destination.scores) ? numericScore(destination.scores[dimension]) : null;
  }

  function statusPriority(status) {
    return { eligible: 0, conditional: 1, needs_verification: 2, not_eligible: 3 }[status] ?? 2;
  }

  function worstStatus() {
    return Array.from(arguments).reduce(function (worst, status) {
      return statusPriority(status) > statusPriority(worst) ? status : worst;
    }, "eligible");
  }

  function retirementCostFor(destinationId, retirementCosts) {
    if (!isObject(retirementCosts)) return null;
    if (isObject(retirementCosts[destinationId])) return retirementCosts[destinationId];
    if (Array.isArray(retirementCosts.destinations)) {
      return retirementCosts.destinations.find(function (row) {
        return isObject(row) && row.destination_id === destinationId;
      }) || null;
    }
    if (Array.isArray(retirementCosts)) {
      return retirementCosts.find(function (row) {
        return isObject(row) && row.destination_id === destinationId;
      }) || null;
    }
    return null;
  }

  function rankDestinations(payload, rawProfile) {
    const input = isObject(payload) ? payload : {};
    const overlay = isObject(input.fire_payload) ? input.fire_payload : input;
    const profile = normalizeProfile(rawProfile === undefined ? input.profile : rawProfile);
    const destinations = Array.isArray(input.destinations) ? input.destinations : [];
    const retirementCosts = input.retirement_costs || input.retirementCosts || {};
    const overrides = isObject(overlay.destination_overrides) ? overlay.destination_overrides : {};
    const countries = isObject(overlay.countries) ? overlay.countries : {};
    const results = [];
    destinations.forEach(function (destination) {
      if (!isObject(destination) || typeof destination.id !== "string") return;
      const destinationId = destination.id;
      const override = isObject(overrides[destinationId]) ? overrides[destinationId] : {};
      const country = isObject(countries[override.country]) ? countries[override.country] : {};
      const eligibility = eligibilityForMode(country, profile);
      const mode = profile.stay_mode;
      const tax = isObject(country.tax) ? country.tax : {};
      const taxModes = isObject(tax.by_mode) ? tax.by_mode : {};
      const taxMode = isObject(taxModes[mode]) ? taxModes[mode] : {};
      const healthcare = isObject(country.healthcare) ? country.healthcare : {};
      const healthcareModes = isObject(healthcare.by_mode) ? healthcare.by_mode : {};
      const healthMode = isObject(healthcareModes[mode]) ? healthcareModes[mode] : {};
      const taxScore = numericScore(taxMode.compatibility_score);
      const healthScore = numericScore(healthMode.bridge_score);
      const taxStatus = typeof taxMode.status === "string" ? taxMode.status : "needs_verification";
      const healthStatus = typeof healthMode.eligibility === "string" ? healthMode.eligibility : "needs_verification";
      const evidenceMissing = taxMode.rankable !== true || taxScore === null || healthScore === null ||
        UNRANKED_STATUSES.has(taxStatus) || UNRANKED_STATUSES.has(healthStatus);
      let status = worstStatus(eligibility.status, taxStatus, healthStatus);
      if (evidenceMissing && status !== "not_eligible") status = "needs_verification";
      const cost = retirementCostFor(destinationId, retirementCosts);
      const budget = buildResilienceBudget(cost || {}, profile, override);
      const exitLiquidity = destinationScore(destination, "exit_liquidity");
      const ownershipClarity = destinationScore(destination, "ownership_clarity");
      const rentFlexibility = numericScore(override.rent_flexibility_score);
      const propertyExit = exitLiquidity === null || ownershipClarity === null || rentFlexibility === null
        ? null : round2((exitLiquidity + ownershipClarity + rentFlexibility) / 3);
      const components = {
        active_life: activeLifeScore(override),
        sustainable_annual_cost: cost ? annualCostScore(budget.annual_total_usd, profile.household) : null,
        healthcare_bridge: healthScore,
        stay_flexibility: eligibility.stay_score,
        tax_compatibility: taxScore,
        global_access: destinationScore(destination, "global_access"),
        community_fit: destinationScore(destination, "foreigner_fit"),
        property_exit_flexibility: propertyExit,
      };
      Object.keys(components).forEach(function (key) {
        if (components[key] !== null) components[key] = round2(components[key]);
      });
      if (Object.keys(components).some(function (key) { return components[key] === null; }) && status !== "not_eligible") {
        status = "needs_verification";
      }
      let score = null;
      if (status === "eligible" || status === "conditional") {
        score = round2(Object.keys(FIRE_WEIGHTS).reduce(function (total, key) {
          return total + components[key] * FIRE_WEIGHTS[key];
        }, 0));
      }
      const warnings = Array.isArray(override.risk_warnings) ? override.risk_warnings.slice() : [];
      if (profile.home_tax_context === "us_person") {
        warnings.push("US persons generally remain subject to U.S. worldwide filing and reporting obligations.");
      }
      if (Number.isInteger(tax.standard_day_threshold) && profile.annual_days !== null && profile.annual_days >= tax.standard_day_threshold) {
        warnings.push("Tax residence likely at the selected day count.");
      }
      if (typeof tax.non_day_tests === "string" && tax.non_day_tests) warnings.push(tax.non_day_tests);
      const activeLife = isObject(override.active_life) ? override.active_life : {};
      let strongest = null;
      Object.keys(activeLife).forEach(function (key) {
        if (strongest === null || (numericScore(activeLife[key]) || 0) > (numericScore(strongest) || 0)) {
          strongest = activeLife[key];
        }
      });
      let statusReason = eligibility.reason;
      if (status === "needs_verification" && evidenceMissing) {
        statusReason = "Tax or healthcare evidence for this stay mode needs verification.";
      }
      results.push({
        destination_id: destinationId,
        name: typeof destination.name === "string" ? destination.name : destinationId,
        status: status,
        status_reason: statusReason,
        score: score,
        components: components,
        resilience_budget: budget,
        work_permission: eligibility.work_permission,
        warnings: warnings,
        strongest_activity_reason: isObject(strongest) && typeof strongest.summary === "string" ? strongest.summary : "",
        activity_tags: Array.isArray(override.activity_tags) ? override.activity_tags.slice() : [],
        confidence: typeof override.confidence === "string" ? override.confidence : "low",
        last_reviewed: override.last_reviewed,
      });
    });
    const confidenceRank = { high: 0, medium_high: 1, medium: 2, low: 3 };
    results.sort(function (left, right) {
      const statusDifference = statusPriority(left.status) - statusPriority(right.status);
      if (statusDifference) return statusDifference;
      const scoreDifference = (right.score === null ? -1 : right.score) - (left.score === null ? -1 : left.score);
      if (scoreDifference) return scoreDifference;
      const confidenceDifference = (confidenceRank[left.confidence] ?? 4) - (confidenceRank[right.confidence] ?? 4);
      if (confidenceDifference) return confidenceDifference;
      return left.name.localeCompare(right.name);
    });
    return results;
  }

  return { normalizeProfile, activeLifeScore, buildResilienceBudget, eligibilityForMode, rankDestinations };
});
