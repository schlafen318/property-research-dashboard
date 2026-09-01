(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxResidence = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const VALID_STATUSES = new Set([
    "likely_home_resident",
    "likely_destination_resident",
    "possible_dual_resident",
    "conditional",
  ]);

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function unique(values) {
    const seen = new Set();
    return values.filter(function (value) {
      if (typeof value !== "string" || value.length === 0 || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }

  function finiteDay(value) {
    if (typeof value === "string" && value.trim() !== "") value = Number(value);
    return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 366
      ? value
      : null;
  }

  function booleanValue(value) {
    if (value === true || value === "true" || value === "yes") return true;
    if (value === false || value === "false" || value === "no") return false;
    return null;
  }

  function sourceIds(item) {
    if (!record(item)) return [];
    const values = Array.isArray(item.source_ids)
      ? item.source_ids
      : Array.isArray(item.sourceIds) ? item.sourceIds : [];
    return unique(values);
  }

  function evaluateTest(profile, rule) {
    const fact = typeof rule.fact === "string" ? rule.fact : "";
    if (!fact || !Object.prototype.hasOwnProperty.call(profile, fact)) return null;
    const value = profile[fact];
    if (value === null || value === undefined || value === "" || value === "unknown") return null;

    if (rule.test === "day_threshold") {
      const day = finiteDay(value);
      const threshold = finiteDay(rule.threshold);
      if (day === null || threshold === null) return null;
      if (rule.operator === "greater_than") return day > threshold;
      if (rule.operator === "less_than") return day < threshold;
      if (rule.operator === "less_than_or_equal") return day <= threshold;
      return day >= threshold;
    }

    if (rule.test === "boolean") {
      const normalized = booleanValue(value);
      if (normalized === null || !Array.isArray(rule.residentValues)) return null;
      return rule.residentValues.indexOf(normalized) !== -1;
    }

    if (rule.test === "side") {
      if (typeof value !== "string" || !Array.isArray(rule.residentValues)) return null;
      if (!["home", "destination", "both", "neither"].includes(value)) return null;
      return rule.residentValues.indexOf(value) !== -1;
    }

    return null;
  }

  function evaluateJurisdiction(profile, rules, side) {
    const list = record(rules) && Array.isArray(rules.rules)
      ? rules.rules.filter(function (rule) {
          return record(rule) && rule.type === "residence_test";
        })
      : [];
    if (list.length === 0) {
      return {
        resident: null,
        unresolvedFacts: [side + "Rules"],
        ruleIds: [],
        sourceIds: [],
        explanations: [{
          code: side + "_rules_unavailable",
          message: "Residence rules are unavailable for the " + side + " jurisdiction.",
          ruleIds: [],
          sourceIds: [],
        }],
      };
    }

    const evaluations = list.map(function (rule) {
      return { rule: rule, outcome: evaluateTest(profile, rule) };
    });
    const positive = evaluations.filter(function (item) { return item.outcome === true; });
    const unknown = evaluations.filter(function (item) { return item.outcome === null; });
    const resident = positive.length > 0 ? true : unknown.length > 0 ? null : false;
    const materialUnknown = resident === null ? unknown : [];

    return {
      resident: resident,
      unresolvedFacts: unique(materialUnknown.map(function (item) { return item.rule.fact; })),
      ruleIds: unique(evaluations.map(function (item) { return item.rule.id; })),
      sourceIds: unique(evaluations.flatMap(function (item) { return sourceIds(item.rule); })),
      explanations: evaluations.map(function (item) {
        const explanation = typeof item.rule.explanation === "string" && item.rule.explanation.trim()
          ? item.rule.explanation.trim()
          : "Residence test evaluated.";
        const outcome = item.outcome === true
          ? " This test indicates domestic residence."
          : item.outcome === false
            ? " This test does not indicate domestic residence."
            : " The controlling fact is unresolved.";
        return {
          code: String(item.rule.id || side + "_residence_test"),
          message: explanation + outcome,
          ruleIds: typeof item.rule.id === "string" ? [item.rule.id] : [],
          sourceIds: sourceIds(item.rule),
        };
      }),
    };
  }

  function scopesFor(status, destinationRules, homeRules) {
    const destinationResident = record(destinationRules) && typeof destinationRules.residentScope === "string"
      ? destinationRules.residentScope : "worldwide_income";
    const destinationNonresident = record(destinationRules) && typeof destinationRules.nonresidentScope === "string"
      ? destinationRules.nonresidentScope : "source_income";
    const homeResident = record(homeRules) && typeof homeRules.residentScope === "string"
      ? homeRules.residentScope : "worldwide_income";
    const homeNonresident = record(homeRules) && typeof homeRules.nonresidentScope === "string"
      ? homeRules.nonresidentScope : "source_income";

    if (status === "likely_destination_resident") {
      return { destination: destinationResident, home: homeNonresident };
    }
    if (status === "likely_home_resident") {
      return { destination: destinationNonresident, home: homeResident };
    }
    if (status === "possible_dual_resident") {
      return { destination: destinationResident, home: homeResident };
    }
    return { destination: "conditional", home: "conditional" };
  }

  function treatyDecision(profile, treaty) {
    if (!record(treaty) || treaty.supported !== true || !Array.isArray(treaty.tests)) {
      return { residence: null, unresolvedFacts: [], reached: false };
    }
    for (const test of treaty.tests) {
      if (!record(test) || typeof test.fact !== "string" || !test.fact) continue;
      const value = profile[test.fact];
      if (value === undefined || value === null || value === "" || value === "unknown") {
        return { residence: null, unresolvedFacts: [test.fact], reached: true };
      }
      if (value === "home" || value === "destination") {
        return { residence: value, unresolvedFacts: [], reached: true };
      }
      if (value !== "both" && value !== "neither") {
        return { residence: null, unresolvedFacts: [test.fact], reached: true };
      }
    }
    return { residence: null, unresolvedFacts: [], reached: true };
  }

  function possibleBranches(profile, destinationResident, homeResident, destinationRules, homeRules) {
    const destinationValues = destinationResident === null ? [false, true] : [destinationResident];
    const homeValues = homeResident === null ? [false, true] : [homeResident];
    const statuses = [];
    destinationValues.forEach(function (destinationValue) {
      homeValues.forEach(function (homeValue) {
        if (destinationValue && !homeValue) {
          statuses.push("likely_destination_resident");
          return;
        }
        if (!destinationValue && homeValue) {
          statuses.push("likely_home_resident");
          return;
        }
        if (!destinationValue && !homeValue) {
          statuses.push("conditional");
          return;
        }
        const treaty = destinationRules.treatyTieBreaker;
        if (!record(treaty) || treaty.supported !== true) {
          statuses.push("possible_dual_resident");
          return;
        }
        const decision = treatyDecision(profile, treaty);
        if (decision.residence === "destination") {
          statuses.push("likely_destination_resident");
        } else if (decision.residence === "home") {
          statuses.push("likely_home_resident");
        } else if (decision.unresolvedFacts.length > 0) {
          statuses.push("likely_home_resident", "likely_destination_resident", "possible_dual_resident");
        } else {
          statuses.push("possible_dual_resident");
        }
      });
    });
    return unique(statuses).map(function (status) {
      return { status: status, scopes: scopesFor(status, destinationRules, homeRules) };
    });
  }

  function validIsoDate(value, year) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const parts = value.split("-").map(Number);
    const time = Date.UTC(parts[0], parts[1] - 1, parts[2]);
    const date = new Date(time);
    if (date.getUTCFullYear() !== parts[0] || date.getUTCMonth() !== parts[1] - 1 || date.getUTCDate() !== parts[2]) {
      return null;
    }
    if (parts[0] !== year) return null;
    return { text: value, time: time };
  }

  function isoDayBefore(time) {
    return new Date(time - 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  }

  function fullYearPeriod(year, status, scopes) {
    return [{
      start: year + "-01-01",
      end: year + "-12-31",
      status: status,
      scopes: Object.assign({}, scopes),
    }];
  }

  function evaluateResidence(profile, destinationRules, homeRules) {
    const safeProfile = record(profile) ? profile : {};
    const destination = record(destinationRules) ? destinationRules : {};
    const home = record(homeRules) ? homeRules : {};
    const configuredYear = Number.isInteger(safeProfile.taxYear)
      ? safeProfile.taxYear
      : Number.isInteger(destination.taxYear)
        ? destination.taxYear
        : Number.isInteger(home.taxYear) ? home.taxYear : 2026;
    const taxYear = configuredYear >= 1900 && configuredYear <= 9999 ? configuredYear : 2026;

    const destinationResult = evaluateJurisdiction(safeProfile, destination, "destination");
    const homeResult = evaluateJurisdiction(safeProfile, home, "home");
    let status = "conditional";
    let treatyResidence = null;
    let unresolvedFacts = destinationResult.unresolvedFacts.concat(homeResult.unresolvedFacts);
    let ruleIds = destinationResult.ruleIds.concat(homeResult.ruleIds);
    let allSourceIds = destinationResult.sourceIds.concat(homeResult.sourceIds);
    let explanations = destinationResult.explanations.concat(homeResult.explanations);

    if (destinationResult.resident === true && homeResult.resident === false) {
      status = "likely_destination_resident";
    } else if (destinationResult.resident === false && homeResult.resident === true) {
      status = "likely_home_resident";
    } else if (destinationResult.resident === true && homeResult.resident === true) {
      const treaty = destination.treatyTieBreaker;
      const decision = treatyDecision(safeProfile, treaty);
      if (record(treaty) && treaty.supported === true) {
        if (typeof treaty.ruleId === "string") ruleIds.push(treaty.ruleId);
        allSourceIds = allSourceIds.concat(sourceIds(treaty));
        explanations.push({
          code: String(treaty.ruleId || "treaty_tie_breaker"),
          message: typeof treaty.explanation === "string" && treaty.explanation.trim()
            ? treaty.explanation.trim()
            : "A supported treaty tie-breaker was evaluated.",
          ruleIds: typeof treaty.ruleId === "string" ? [treaty.ruleId] : [],
          sourceIds: sourceIds(treaty),
        });
      }
      if (decision.residence === "destination") {
        status = "likely_destination_resident";
        treatyResidence = "destination";
      } else if (decision.residence === "home") {
        status = "likely_home_resident";
        treatyResidence = "home";
      } else if (decision.unresolvedFacts.length > 0) {
        status = "conditional";
        unresolvedFacts = unresolvedFacts.concat(decision.unresolvedFacts);
      } else {
        status = "possible_dual_resident";
      }
    } else if (destinationResult.resident === false && homeResult.resident === false) {
      status = "conditional";
      unresolvedFacts.push("residenceOutcome");
    }

    let scopes = scopesFor(status, destination, home);
    let periods = fullYearPeriod(taxYear, status, scopes);
    const split = destination.splitYear;
    const splitRequested = safeProfile.splitYear === true ||
      (record(split) && typeof split.dateFact === "string" &&
        Object.prototype.hasOwnProperty.call(safeProfile, split.dateFact));
    if (splitRequested && record(split) && split.supported === true) {
      if (typeof split.ruleId === "string") ruleIds.push(split.ruleId);
      allSourceIds = allSourceIds.concat(sourceIds(split));
      explanations.push({
        code: String(split.ruleId || "split_year"),
        message: typeof split.explanation === "string" && split.explanation.trim()
          ? split.explanation.trim()
          : "A supported split-year rule was evaluated.",
        ruleIds: typeof split.ruleId === "string" ? [split.ruleId] : [],
        sourceIds: sourceIds(split),
      });
      const dateFact = typeof split.dateFact === "string" ? split.dateFact : "moveDate";
      const move = validIsoDate(safeProfile[dateFact], taxYear);
      if (move === null) {
        status = "conditional";
        unresolvedFacts.push(dateFact);
        scopes = scopesFor(status, destination, home);
        periods = fullYearPeriod(taxYear, status, scopes);
      } else if (status === "likely_destination_resident" && move.text !== taxYear + "-01-01") {
        periods = [
          {
            start: taxYear + "-01-01",
            end: isoDayBefore(move.time),
            status: "likely_home_resident",
            scopes: scopesFor("likely_home_resident", destination, home),
          },
          {
            start: move.text,
            end: taxYear + "-12-31",
            status: "likely_destination_resident",
            scopes: scopesFor("likely_destination_resident", destination, home),
          },
        ];
      }
    } else if (splitRequested && (!record(split) || split.supported !== true)) {
      status = "conditional";
      unresolvedFacts.push("splitYearTreatment");
      scopes = scopesFor(status, destination, home);
      periods = fullYearPeriod(taxYear, status, scopes);
    }

    unresolvedFacts = unique(unresolvedFacts);
    ruleIds = unique(ruleIds);
    allSourceIds = unique(allSourceIds);
    const branches = status === "conditional"
      ? possibleBranches(
          safeProfile,
          destinationResult.resident,
          homeResult.resident,
          destination,
          home
        )
      : [];

    if (!VALID_STATUSES.has(status)) status = "conditional";
    return {
      status: status,
      taxYear: taxYear,
      domesticResidence: {
        destination: destinationResult.resident,
        home: homeResult.resident,
      },
      treatyResidence: treatyResidence,
      periods: periods,
      scopes: scopes,
      unresolvedFacts: unresolvedFacts,
      materialFacts: unresolvedFacts.slice(),
      branches: branches,
      explanations: explanations,
      ruleIds: ruleIds,
      sourceIds: allSourceIds,
    };
  }

  return { evaluateResidence: evaluateResidence };
});
