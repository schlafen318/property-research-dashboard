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
  const REQUIRED_RETIREMENT_CATEGORIES = new Set([
    "food_household", "utilities_communications", "private_healthcare", "transport",
    "dining_leisure", "travel", "visa_admin", "contingency",
  ]);
  const UNRANKED_STATUSES = new Set(["needs_verification", "not_eligible"]);
  const VALID_ELIGIBILITY = new Set(["eligible", "conditional", "needs_verification", "not_eligible"]);
  const VALID_WORK_PERMISSIONS = new Set(["passive_only", "remote_permitted", "local_permitted", "unclear"]);
  const VALID_CONFIDENCE = new Set(["low", "medium", "medium_high", "high"]);
  const CONFIDENCE_PRIORITY = { low: 0, medium: 1, medium_high: 2, high: 3 };

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function isNumber(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function round2(value) {
    const scaled = value * 100;
    const tolerance = Number.EPSILON * Math.max(1, Math.abs(scaled)) * 4;
    return Math.floor(scaled + 0.5 + tolerance) / 100;
  }

  function nonnegativeNumber(value) {
    return isNumber(value) && value >= 0;
  }

  function workPermissionLabel(value) {
    return {
      passive_only: "Passive income only",
      remote_permitted: "Remote work permitted",
      local_permitted: "Local work permitted",
      unclear: "Work permission needs professional review",
    }[String(value)] || "Work permission needs professional review";
  }

  function eligibilityLabel(value) {
    return {
      eligible: "Eligible",
      conditional: "Conditional",
      needs_verification: "Needs verification",
      not_eligible: "Not currently eligible",
    }[String(value)] || "Needs verification";
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
    if (!isObject(activeLife)) return null;
    let total = 0;
    for (const component of Object.keys(ACTIVE_LIFE_WEIGHTS)) {
      const score = numericScore(activeLife[component]);
      if (score === null) return null;
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
        max_days: null,
        confidence: "low",
        last_reviewed: null,
      };
    }
    let status = route.status;
    let summary = typeof route.summary === "string" && route.summary ? route.summary : "Route conditions require confirmation.";
    const selected = isObject(route.mobility_rights) && isObject(route.mobility_rights[normalized.mobility_rights])
      ? route.mobility_rights[normalized.mobility_rights] : null;
    if (!selected) {
      return {
        status: "needs_verification",
        reason: "Nationality-dependent mobility rights must be confirmed.",
        work_permission: "unclear",
        stay_score: null,
        max_days: null,
        confidence: typeof route.confidence === "string" ? route.confidence : "low",
        last_reviewed: typeof route.last_reviewed === "string" ? route.last_reviewed : null,
      };
    }
    status = selected.status;
    let score = isNumber(selected.base_score) ? selected.base_score : null;
    const maxDays = Number.isInteger(selected.max_days) ? selected.max_days : null;
    const workPermission = VALID_WORK_PERMISSIONS.has(selected.work_permission) ? selected.work_permission : "unclear";
    if (normalized.mobility_rights !== "local_free_movement" && Number.isInteger(route.minimum_age) && normalized.age < route.minimum_age) {
      return {
        status: "not_eligible",
        reason: "This route requires an age of at least " + route.minimum_age + ".",
        work_permission: workPermission,
        stay_score: 0,
        max_days: maxDays,
        confidence: typeof route.confidence === "string" ? route.confidence : "low",
        last_reviewed: typeof route.last_reviewed === "string" ? route.last_reviewed : null,
      };
    }
    if (Number.isInteger(normalized.annual_days) && maxDays !== null && normalized.annual_days > maxDays) {
      if (normalized.mobility_rights === "general_nonlocal") {
        status = "not_eligible";
        summary = "The selected " + normalized.annual_days + " days exceed this route's " + maxDays + "-day cap.";
      } else {
        status = "needs_verification";
        summary = "The selected " + normalized.annual_days + " days exceed the documented " + maxDays + "-day cap; mobility rights need verification.";
      }
    }
    if (!VALID_ELIGIBILITY.has(status)) status = "needs_verification";
    if (UNRANKED_STATUSES.has(status) || score === null) score = null;
    else {
      if (normalized.income_type === "business_consulting") {
        if (workPermission === "passive_only") score -= 0.5;
        else if (workPermission === "unclear") score -= 1;
      }
      score = round2(Math.max(0, Math.min(5, score)));
    }
    return {
      status: status,
      reason: summary,
      work_permission: workPermission,
      stay_score: score,
      max_days: maxDays,
      confidence: typeof route.confidence === "string" ? route.confidence : "low",
      last_reviewed: typeof route.last_reviewed === "string" ? route.last_reviewed : null,
    };
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
    const usable = hasUsableCost(source, normalized);
    const categories = {};
    Object.keys(rawCategories).forEach(function (key) {
      if (usable && REQUIRED_RETIREMENT_CATEGORIES.has(key) && nonnegativeNumber(rawCategories[key])) {
        categories[key] = rawCategories[key];
      }
    });
    const rents = normalized.housing === "rent" || normalized.housing === "buy_retirement";
    const housingCost = rents ? householdCost.annual_rent_usd : householdCost.annual_owner_costs_usd;
    if (usable && nonnegativeNumber(housingCost)) categories[rents ? "rent" : "owner_costs"] = housingCost;
    const property = isObject(source.property) ? source.property : {};
    let propertyCapital = 0;
    if (normalized.housing === "buy_now" || normalized.housing === "buy_retirement") {
      propertyCapital = null;
      if (usable && nonnegativeNumber(property.representative_price_usd) && property.representative_price_usd > 0 && nonnegativeNumber(property.acquisition_cost_rate)) {
        propertyCapital = round2(property.representative_price_usd * (1 + property.acquisition_cost_rate));
      }
    }
    const recurringWithoutContingency = Object.keys(categories).reduce(function (total, key) {
      return total + (key === "contingency" ? 0 : categories[key]);
    }, 0);
    const bufferRaw = recurringWithoutContingency * 0.10;
    const bufferTolerance = Number.EPSILON * Math.max(1, Math.abs(bufferRaw)) * 4;
    const currencyInflationBuffer = usable ? Math.floor(bufferRaw + 0.5 + bufferTolerance) : null;
    const annualTotal = usable ? round2(Object.keys(categories).reduce(function (total, key) {
      return total + categories[key];
    }, 0) + currencyInflationBuffer) : null;
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

  function compareCodePoints(left, right) {
    const first = String(left);
    const second = String(right);
    let firstIndex = 0;
    let secondIndex = 0;
    while (firstIndex < first.length && secondIndex < second.length) {
      const firstPoint = first.codePointAt(firstIndex);
      const secondPoint = second.codePointAt(secondIndex);
      if (firstPoint !== secondPoint) return firstPoint < secondPoint ? -1 : 1;
      firstIndex += firstPoint > 0xFFFF ? 2 : 1;
      secondIndex += secondPoint > 0xFFFF ? 2 : 1;
    }
    return firstIndex === first.length && secondIndex === second.length ? 0 : (firstIndex === first.length ? -1 : 1);
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

  function hasUsableCost(cost, profile) {
    if (!isObject(cost) || !isObject(cost.profiles)) return false;
    const householdCost = cost.profiles[profile.household];
    if (!isObject(householdCost) || !isObject(householdCost.categories_usd)) return false;
    for (const category of REQUIRED_RETIREMENT_CATEGORIES) {
      if (!Object.prototype.hasOwnProperty.call(householdCost.categories_usd, category) ||
          !nonnegativeNumber(householdCost.categories_usd[category])) return false;
    }
    const housingCost = profile.housing === "rent" || profile.housing === "buy_retirement"
      ? householdCost.annual_rent_usd : householdCost.annual_owner_costs_usd;
    if (!nonnegativeNumber(housingCost)) return false;
    if (profile.housing === "buy_now" || profile.housing === "buy_retirement") {
      if (!isObject(cost.property) || !nonnegativeNumber(cost.property.representative_price_usd) ||
          cost.property.representative_price_usd <= 0 || !nonnegativeNumber(cost.property.acquisition_cost_rate)) {
        return false;
      }
    }
    return true;
  }

  function normalizeConfidence(value) {
    if (typeof value !== "string") return null;
    const normalized = value.trim().toLowerCase().replace(/[- ]/g, "_");
    return VALID_CONFIDENCE.has(normalized) ? normalized : null;
  }

  function conservativeConfidence(values) {
    const normalized = values.map(normalizeConfidence);
    if (!normalized.length || normalized.some(function (value) { return value === null; })) return "low";
    return normalized.reduce(function (lowest, value) {
      return CONFIDENCE_PRIORITY[value] < CONFIDENCE_PRIORITY[lowest] ? value : lowest;
    });
  }

  function validIsoDate(value) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const parsed = new Date(value + "T00:00:00Z");
    return Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value ? null : value;
  }

  function earliestReviewDate(values) {
    if (!values.length) return null;
    const dates = values.map(validIsoDate);
    if (dates.some(function (value) { return value === null; })) return null;
    dates.sort();
    return dates.length ? dates[0] : null;
  }

  function taxIncomeCategory(flags, incomeType) {
    const source = isObject(flags) ? flags : {};
    const keys = {
      portfolio: ["dividends", "capital_gains"],
      pension: ["pensions"],
      property: ["property_income"],
      mixed: ["pensions", "dividends", "capital_gains", "property_income"],
    }[incomeType];
    if (!keys) {
      if (incomeType === "business_consulting") {
        return "Business or consulting income, work location, and permanent-establishment questions need professional review.";
      }
      return "Income-category treatment depends on the selected income mix.";
    }
    const selected = keys.map(function (key) { return source[key]; }).filter(function (value) {
      return typeof value === "string" && value;
    });
    return selected.join(" ") || "Income-category treatment needs jurisdiction-specific review.";
  }

  function selectedEvidence(eligibility, tax, taxMode, healthMode, financial, override, cost, profile) {
    const confidenceRecord = isObject(cost) ? cost.confidence : null;
    const costConfidence = isObject(confidenceRecord) ? confidenceRecord.overall : confidenceRecord;
    const activeLife = isObject(override.active_life) ? override.active_life : {};
    const confidences = [
      override.confidence, eligibility.confidence, tax.confidence, healthMode.confidence,
      financial.confidence, costConfidence,
    ];
    Object.keys(ACTIVE_LIFE_WEIGHTS).forEach(function (component) {
      confidences.push(isObject(activeLife[component]) ? activeLife[component].confidence : null);
    });
    const reviewDates = [
      override.last_reviewed, eligibility.last_reviewed, tax.last_reviewed,
      healthMode.last_reviewed, financial.last_reviewed,
    ];
    if (isObject(cost) && Array.isArray(cost.sources)) {
      cost.sources.forEach(function (source) {
        reviewDates.push(isObject(source) ? source.accessed_on : null);
      });
    }
    if (!isObject(cost) || !Array.isArray(cost.sources) || !cost.sources.length) reviewDates.push(null);
    const banking = [financial.bank_account_opening, financial.tax_id_dependency].filter(function (part) {
      return typeof part === "string" && part;
    }).join(" ");
    const transfers = [financial.international_transfer_friction, financial.international_payments].filter(function (part) {
      return typeof part === "string" && part;
    }).join(" ");
    return {
      stay_facts: {
        summary: eligibility.reason || "Route conditions require confirmation.",
        max_days: eligibility.max_days,
        work_permission: workPermissionLabel(eligibility.work_permission),
      },
      tax_facts: {
        summary: taxMode.summary || "Selected-mode tax residence needs a separate review.",
        scope_if_resident: tax.scope_if_resident || "Resident scope needs jurisdiction-specific review.",
        income_category: taxIncomeCategory(tax.category_flags, profile.income_type),
        treaty_reporting: tax.treaty_reporting_note || "Treaty relief and reporting need professional review.",
      },
      healthcare_facts: {
        eligibility: eligibilityLabel(healthMode.eligibility),
        waiting_period: healthMode.waiting_period_summary || "Waiting-period and access rules need verification.",
        age_limits: healthMode.age_limit_summary || "Age limits need verification.",
        pre_existing_conditions: healthMode.pre_existing_condition_summary || "Pre-existing-condition terms need verification.",
        evacuation: healthMode.evacuation_summary || "Evacuation and repatriation cover need verification.",
      },
      financial_infrastructure_facts: {
        banking: banking || "Bank-account access needs verification.",
        transfers: transfers || "International transfer access needs verification.",
        brokerage: financial.brokerage_access || "Brokerage access needs verification after a tax-home change.",
      },
      confidence: conservativeConfidence(confidences),
      last_reviewed: earliestReviewDate(reviewDates),
    };
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
      const financial = isObject(country.financial_infrastructure) ? country.financial_infrastructure : {};
      const taxScore = numericScore(taxMode.compatibility_score);
      const healthScore = numericScore(healthMode.bridge_score);
      const taxStatus = typeof taxMode.status === "string" ? taxMode.status : "needs_verification";
      const healthStatus = typeof healthMode.eligibility === "string" ? healthMode.eligibility : "needs_verification";
      const evidenceMissing = taxMode.rankable !== true || taxScore === null || healthScore === null ||
        UNRANKED_STATUSES.has(taxStatus) || UNRANKED_STATUSES.has(healthStatus);
      let status = worstStatus(eligibility.status, taxStatus, healthStatus);
      if (evidenceMissing && status !== "not_eligible") status = "needs_verification";
      const cost = retirementCostFor(destinationId, retirementCosts);
      const usableCost = hasUsableCost(cost, profile);
      const budget = buildResilienceBudget(cost || {}, profile, override);
      const exitLiquidity = destinationScore(destination, "exit_liquidity");
      const ownershipClarity = destinationScore(destination, "ownership_clarity");
      const rentFlexibility = numericScore(override.rent_flexibility_score);
      const propertyExit = exitLiquidity === null || ownershipClarity === null || rentFlexibility === null
        ? null : round2((exitLiquidity + ownershipClarity + rentFlexibility) / 3);
      const components = {
        active_life: activeLifeScore(override),
        sustainable_annual_cost: usableCost && budget.annual_total_usd !== null
          ? annualCostScore(budget.annual_total_usd, profile.household) : null,
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
      const evidence = selectedEvidence(
        eligibility, tax, taxMode, healthMode, financial, override, cost, profile
      );
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
        stay_facts: evidence.stay_facts,
        tax_facts: evidence.tax_facts,
        healthcare_facts: evidence.healthcare_facts,
        financial_infrastructure_facts: evidence.financial_infrastructure_facts,
        confidence: evidence.confidence,
        last_reviewed: evidence.last_reviewed,
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
      return compareCodePoints(left.name, right.name);
    });
    return results;
  }

  return { normalizeProfile, activeLifeScore, buildResilienceBudget, eligibilityForMode, rankDestinations };
});
