(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireAbroad = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const sets = {
    stay_mode: new Set(["seasonal", "part_year", "full_relocation"]),
    household: new Set(["single", "couple"]),
    housing: new Set(["rent", "own", "buy_now", "buy_retirement"]),
    tax_mode: new Set(["destination_estimate", "user_after_tax"]),
    funding_source: new Set(["portfolio", "pension", "property", "work_business", "mixed"]),
    property_use: new Set(["personal", "rental", "mixed"]),
    annual_day_band: new Set(["under_90", "90_182", "183_plus", "unsure"]),
    mobility_rights: new Set(["local_free_movement", "general_nonlocal", "prefer_not_to_say"]),
    home_tax_context: new Set(["citizenship_based_worldwide", "residence_based", "territorial", "prefer_not_to_say"]),
  };
  const weights = {
    active_life: 0.25,
    sustainable_annual_cost: 0.20,
    healthcare_bridge: 0.15,
    stay_flexibility: 0.10,
    tax_readiness: 0.10,
    global_access: 0.08,
    community_fit: 0.07,
    property_exit_flexibility: 0.05,
  };

  function selected(value, key, fallback) {
    const candidate = value === undefined || value === null || value === "" ? fallback : String(value);
    if (!sets[key].has(candidate)) throw new Error(key + " is invalid");
    return candidate;
  }

  function normalizeProfile(raw) {
    raw = raw || {};
    let planningBase = raw.planning_base;
    if (planningBase === undefined || planningBase === null || planningBase === "") {
      planningBase = null;
    } else {
      planningBase = Number(planningBase);
      if (!Number.isFinite(planningBase) || planningBase < 0) throw new Error("planning_base must be non-negative");
    }
    const age = raw.age === undefined || raw.age === null || raw.age === "" ? 50 : Number(raw.age);
    if (!Number.isFinite(age) || age < 18 || age > 100) throw new Error("age must be between 18 and 100");
    return {
      stay_mode: selected(raw.stay_mode, "stay_mode", "part_year"),
      age: age,
      household: selected(raw.household, "household", "single"),
      housing: selected(raw.housing, "housing", "rent"),
      tax_mode: selected(raw.tax_mode, "tax_mode", "destination_estimate"),
      funding_source: selected(raw.funding_source, "funding_source", "portfolio"),
      property_use: selected(raw.property_use, "property_use", "personal"),
      annual_day_band: selected(raw.annual_day_band, "annual_day_band", "unsure"),
      mobility_rights: selected(raw.mobility_rights, "mobility_rights", "prefer_not_to_say"),
      home_tax_context: selected(raw.home_tax_context, "home_tax_context", "prefer_not_to_say"),
      planning_base: planningBase,
    };
  }

  function screenTax(input) {
    const country = input && input.country || {};
    const profile = normalizeProfile(input && input.profile || {});
    const screen = country.tax_screen || {};
    if (screen.status !== "complete") {
      return {
        status: "tax_impact_unavailable",
        conditional: true,
        residence_outcome: "needs_evidence",
        scope_summary: "Tax-impact research is not complete for this destination.",
        readiness: "highly_profile_dependent",
        readiness_score: null,
        favorable_reserve: null,
        central_reserve: null,
        adverse_reserve: null,
        rates: null,
        included_categories: [],
        material_flags: [],
        source_ids: [],
        confidence: "low",
      };
    }
    const band = screen.planning_bands[profile.stay_mode];
    const rates = {
      favorable: Number(band.favorable_rate),
      central: Number(band.central_rate),
      adverse: Number(band.adverse_rate),
    };
    const bypass = profile.tax_mode === "user_after_tax";
    function reserve(key) {
      if (bypass) return 0;
      return profile.planning_base === null ? null : Math.round(profile.planning_base * rates[key]);
    }
    const residence = {
      under_90: "likely_nonresident",
      "90_182": "residence_depends_on_days_and_ties",
      "183_plus": "likely_resident",
      unsure: "residence_depends_on_days_and_ties",
    }[profile.annual_day_band];
    const fallbackFundingNotes = {
      portfolio: "Portfolio income needs category-specific review.",
      pension: "Pension income needs treaty and pension-type review.",
      property: "Property income needs source-country and residence review.",
      work_business: "Work or business income needs source and social-tax review.",
      mixed: "Each income category needs separate review.",
    };
    const fundingNote = (screen.funding_source_notes || {})[profile.funding_source] ||
      fallbackFundingNotes[profile.funding_source];
    const materialFlags = (screen.material_flags || []).slice();
    if (profile.housing !== "rent" && (profile.property_use === "rental" || profile.property_use === "mixed")) {
      materialFlags.push("property_rental_tax");
    }
    if (profile.home_tax_context === "citizenship_based_worldwide") {
      materialFlags.push("continuing_home_country_tax");
    } else if (profile.home_tax_context === "prefer_not_to_say") {
      materialFlags.push("home_country_tax_interaction");
    }
    return {
      status: bypass ? "user_after_tax" : "planning_estimate",
      conditional: residence === "residence_depends_on_days_and_ties" ||
        profile.home_tax_context === "citizenship_based_worldwide" ||
        profile.home_tax_context === "prefer_not_to_say",
      residence_outcome: residence,
      scope_summary: fundingNote + " " + (screen.scope_if_resident === "worldwide_income"
        ? "Worldwide income may enter scope if destination tax residence applies."
        : "Local-source income may remain taxable."),
      readiness: screen.tax_readiness,
      readiness_score: Number(screen.tax_readiness_score),
      favorable_reserve: reserve("favorable"),
      central_reserve: reserve("central"),
      adverse_reserve: reserve("adverse"),
      rates: rates,
      included_categories: (screen.included_categories || []).slice(),
      material_flags: materialFlags,
      source_ids: (screen.source_ids || []).slice(),
      confidence: screen.confidence || "low",
    };
  }

  function screenEligibility(input) {
    const country = input && input.country || {};
    const profile = normalizeProfile(input && input.profile || {});
    const evidence = country.eligibility || {};
    if (evidence.status !== "complete") {
      return { status: "needs_verification", rankable: false, summary: "Legal-stay evidence is not complete for this destination.", source_ids: [] };
    }
    if (profile.mobility_rights === "local_free_movement") {
      return { status: "likely_eligible", rankable: true, summary: "Local or free-movement rights provide a credible stay path; registration rules may still apply.", source_ids: (evidence.long_stay_source_ids || []).slice() };
    }
    if (profile.mobility_rights === "general_nonlocal" && profile.annual_day_band === "under_90") {
      return { status: "eligibility_depends_on_profile", rankable: false, summary: "A short stay may fit the general visitor limit, but passport and visa rules still control.", source_ids: (evidence.short_stay_source_ids || []).slice() };
    }
    return { status: "eligibility_depends_on_profile", rankable: false, summary: "A visa or residence route must be verified for this stay plan.", source_ids: (evidence.long_stay_source_ids || []).slice() };
  }

  function buildResilienceBudget(input) {
    const profile = normalizeProfile(input && input.profile || {});
    const cost = input && input.cost || {};
    const taxScreen = input && input.taxScreen || {};
    const household = cost.profiles && cost.profiles[profile.household];
    if (!household) throw new Error("Missing household retirement-cost profile");
    const categories = household.categories_usd || {};
    const recurring = Object.keys(categories).reduce(function (total, key) {
      return total + Number(categories[key]);
    }, 0);
    const housing = profile.housing === "rent"
      ? Number(household.annual_rent_usd || 0)
      : Number(household.annual_owner_costs_usd || 0);
    const base = recurring + housing;
    if (taxScreen.status === "tax_impact_unavailable") {
      return {
        base_annual_cost: Math.round(base),
        favorable_annual_cost: null,
        central_annual_cost: null,
        adverse_annual_cost: null,
        conditional: true,
      };
    }
    const reserveBase = profile.planning_base === null ? base : profile.planning_base;
    const bypass = profile.tax_mode === "user_after_tax";
    const reserves = {};
    ["favorable", "central", "adverse"].forEach(function (key) {
      reserves[key] = bypass ? 0 : Math.round(reserveBase * Number(taxScreen.rates[key]));
    });
    return {
      base_annual_cost: Math.round(base),
      favorable_tax_reserve: reserves.favorable,
      central_tax_reserve: reserves.central,
      adverse_tax_reserve: reserves.adverse,
      favorable_annual_cost: Math.round(base + reserves.favorable),
      central_annual_cost: Math.round(base + reserves.central),
      adverse_annual_cost: Math.round(base + reserves.adverse),
      conditional: Boolean(taxScreen.conditional),
    };
  }

  function rankDestinations(input) {
    input = input || {};
    const profile = normalizeProfile(input.profile || {});
    const firePayload = input.firePayload || {};
    const countries = firePayload.countries || {};
    const overrides = firePayload.destination_overrides || {};
    const costs = input.retirementCosts || {};
    const rows = (input.destinations || []).map(function (destination) {
      const override = overrides[destination.id] || {};
      const countryName = override.country || destination.country;
      const country = countries[countryName] || { tax_screen: { status: "research_pending" } };
      const eligibility = screenEligibility({ country: country, profile: profile });
      const tax = screenTax({ country: country, profile: profile });
      const cost = costs[destination.id];
      const rankable = Boolean(cost && override.scores && eligibility.rankable && tax.status !== "tax_impact_unavailable");
      return {
        destination_id: destination.id,
        name: destination.name || destination.id,
        country: countryName,
        rankable: rankable,
        eligibility: eligibility,
        overall_score: null,
        tax: tax,
        budget: cost ? buildResilienceBudget({ cost: cost, profile: profile, taxScreen: tax }) : null,
        scores: override.scores || {},
      };
    });
    const rankableRows = rows.filter(function (row) { return row.rankable; });
    const values = rankableRows.map(function (row) { return row.budget.central_annual_cost; });
    const low = values.length ? Math.min.apply(null, values) : 0;
    const high = values.length ? Math.max.apply(null, values) : 0;
    rankableRows.forEach(function (row) {
      const costScore = low === high ? 3 : 5 - 4 * (row.budget.central_annual_cost - low) / (high - low);
      const dimensions = {
        active_life: Number(row.scores.active_life),
        sustainable_annual_cost: costScore,
        healthcare_bridge: Number(row.scores.healthcare_bridge),
        stay_flexibility: Number(row.scores.stay_flexibility),
        tax_readiness: Number(row.tax.readiness_score),
        global_access: Number(row.scores.global_access),
        community_fit: Number(row.scores.community_fit),
        property_exit_flexibility: Number(row.scores.property_exit_flexibility),
      };
      const score = Object.keys(weights).reduce(function (total, key) {
        return total + dimensions[key] * weights[key];
      }, 0);
      row.dimension_scores = dimensions;
      row.overall_score = Math.round(score * 100) / 100;
    });
    return rows.sort(function (left, right) {
      if (left.rankable !== right.rankable) return left.rankable ? -1 : 1;
      if (left.rankable && left.overall_score !== right.overall_score) {
        return right.overall_score - left.overall_score;
      }
      return left.name.localeCompare(right.name);
    });
  }

  return {
    normalizeProfile: normalizeProfile,
    screenTax: screenTax,
    screenEligibility: screenEligibility,
    buildResilienceBudget: buildResilienceBudget,
    rankDestinations: rankDestinations,
  };
});
