(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxResidence = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const STATUSES = new Set(["likely_home_resident", "likely_destination_resident", "possible_dual_resident", "conditional"]);
  const SCOPES = new Set(["worldwide_income", "source_income", "conditional"]);
  const FORMULA_OPERATIONS = new Set(["greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "equals", "not_equals", "flag"]);
  const CONDITION_OPERATORS = new Set(["equals", "not_equals", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "in"]);

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function unique(values) {
    const seen = new Set();
    return values.filter(function (value) {
      if (typeof value !== "string" || !value || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }

  function sourceIds(item) {
    return record(item) && Array.isArray(item.source_ids)
      ? unique(item.source_ids)
      : [];
  }

  function daysInYear(year) {
    return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 366 : 365;
  }

  function parseDate(value) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const parts = value.split("-").map(Number);
    const time = Date.UTC(parts[0], parts[1] - 1, parts[2]);
    const parsed = new Date(time);
    if (parsed.getUTCFullYear() !== parts[0] || parsed.getUTCMonth() !== parts[1] - 1 || parsed.getUTCDate() !== parts[2]) return null;
    return { text: value, year: parts[0], time: time };
  }

  function validScopePair(value) {
    return record(value) &&
      Object.keys(value).length === 2 &&
      SCOPES.has(value.destination) &&
      SCOPES.has(value.home);
  }

  function scopesMatchStatus(status, scopes) {
    const expected = status === "likely_destination_resident"
      ? { destination: "worldwide_income", home: "source_income" }
      : status === "likely_home_resident"
        ? { destination: "source_income", home: "worldwide_income" }
        : status === "possible_dual_resident"
          ? { destination: "worldwide_income", home: "worldwide_income" }
          : { destination: "conditional", home: "conditional" };
    return validScopePair(scopes) && scopes.destination === expected.destination && scopes.home === expected.home;
  }

  function valueMatchesType(value, valueType) {
    if (valueType === "number" || valueType === "money") return typeof value === "number" && Number.isFinite(value);
    if (valueType === "boolean") return typeof value === "boolean";
    if (valueType === "string") return typeof value === "string";
    if (valueType === "date") return parseDate(value) !== null;
    return false;
  }

  function validOperand(operand) {
    if (!record(operand) || !["profile", "constant", "derived"].includes(operand.kind) || !["number", "money", "boolean", "string", "date"].includes(operand.value_type)) return false;
    if (operand.value_type === "money" && (typeof operand.currency !== "string" || !/^[A-Z]{3}$/.test(operand.currency))) return false;
    if (operand.kind === "constant" && (!Object.prototype.hasOwnProperty.call(operand, "value") || !valueMatchesType(operand.value, operand.value_type))) return false;
    if (operand.kind === "profile" && (typeof operand.profile_key !== "string" || !/^[A-Za-z][A-Za-z0-9]*$/.test(operand.profile_key))) return false;
    if (Object.prototype.hasOwnProperty.call(operand, "minimum") && (operand.value_type !== "number" || typeof operand.minimum !== "number" || !Number.isFinite(operand.minimum))) return false;
    if (Object.prototype.hasOwnProperty.call(operand, "maximum") && (operand.value_type !== "number" || typeof operand.maximum !== "number" || !Number.isFinite(operand.maximum))) return false;
    if (typeof operand.minimum === "number" && typeof operand.maximum === "number" && operand.minimum > operand.maximum) return false;
    if (Object.prototype.hasOwnProperty.call(operand, "integer") && (operand.value_type !== "number" || typeof operand.integer !== "boolean")) return false;
    if (Object.prototype.hasOwnProperty.call(operand, "day_count") && (operand.kind !== "profile" || operand.value_type !== "number" || operand.day_count !== true)) return false;
    if (Object.prototype.hasOwnProperty.call(operand, "allowed_values")) {
      if (operand.kind !== "profile" || operand.value_type !== "string" || !Array.isArray(operand.allowed_values) || operand.allowed_values.length < 2 ||
          !operand.allowed_values.every(function (value) { return typeof value === "string" && value.length > 0; }) || new Set(operand.allowed_values).size !== operand.allowed_values.length) return false;
    }
    return operand.kind !== "derived";
  }

  function validActiveOperand(operand) {
    return validOperand(operand) && !(operand.kind === "profile" && operand.value_type === "string" && !Array.isArray(operand.allowed_values));
  }

  function validDatedAudit(recordValue, payloadDate) {
    if (!record(recordValue) || typeof recordValue.effective_from !== "string" || typeof recordValue.checked_on !== "string") return false;
    const effective = parseDate(recordValue.effective_from);
    const checked = parseDate(recordValue.checked_on);
    if (!effective || !checked || effective.time > checked.time || checked.time > payloadDate.time || !Number.isInteger(recordValue.review_interval_days) || recordValue.review_interval_days <= 0) return false;
    return (payloadDate.time - checked.time) / 86400000 <= recordValue.review_interval_days;
  }

  function validSource(source, payloadDate) {
    return validDatedAudit(source, payloadDate) && typeof source.id === "string" && source.id.length > 0 &&
      typeof source.publisher === "string" && source.publisher.trim().length > 0 &&
      typeof source.url === "string" && /^https:\/\/[^/]+/.test(source.url) &&
      ["official", "primary", "synthetic"].includes(source.source_kind) &&
      typeof source.scope === "string" && source.scope.trim().length > 0 &&
      typeof source.recheck_trigger === "string" && source.recheck_trigger.trim().length > 0;
  }

  function validRuleAudit(rule, payload, payloadDate, knownSources) {
    return record(rule) && typeof rule.id === "string" && rule.id.endsWith("-" + payload.tax_year) &&
      rule.tax_year === payload.tax_year && Array.isArray(rule.taxpayer_scope) && rule.taxpayer_scope.length > 0 && rule.taxpayer_scope.every(function (scope) { return typeof scope === "string" && scope.length > 0; }) &&
      typeof rule.category === "string" && rule.category.length > 0 && typeof rule.currency === "string" && /^[A-Z]{3}$/.test(rule.currency) &&
      Array.isArray(rule.source_ids) && rule.source_ids.length > 0 && rule.source_ids.every(function (id) { return knownSources.has(id); }) &&
      validDatedAudit(rule, payloadDate) && ["high", "medium", "low"].includes(rule.confidence) &&
      typeof rule.recheck_trigger === "string" && rule.recheck_trigger.trim().length > 0 &&
      typeof rule.explanation === "string" && rule.explanation.trim().length > 0;
  }

  function ruleUsesOperand(rule, operandId) {
    const formula = record(rule.formula) ? rule.formula : {};
    if (Array.isArray(formula.operands) && formula.operands.indexOf(operandId) !== -1) return true;
    if (rule.date_operand === operandId || rule.activation_operand === operandId) return true;
    return Array.isArray(rule.branches) && rule.branches.some(function (branch) {
      return record(branch) && record(branch.when) && branch.when.operand === operandId;
    });
  }

  function validFormula(formula, catalog, allowedOperations) {
    if (!record(formula) || !allowedOperations.has(formula.operation) || !Array.isArray(formula.operands)) return false;
    const expected = formula.operation === "flag" ? 1 : 2;
    if (formula.operands.length !== expected || !formula.operands.every(function (operandId) {
      return typeof operandId === "string" && validActiveOperand(catalog[operandId]);
    })) return false;
    const operands = formula.operands.map(function (operandId) { return catalog[operandId]; });
    if (formula.operation === "flag") return operands[0].value_type === "boolean";
    const sameType = operands[0].value_type === operands[1].value_type;
    const sameCurrency = operands[0].value_type !== "money" || operands[0].currency === operands[1].currency;
    if (["equals", "not_equals"].includes(formula.operation)) return sameType && sameCurrency;
    return sameType && sameCurrency && ["number", "money", "date"].includes(operands[0].value_type);
  }

  function valueMatchesOperand(value, operand) {
    return valueMatchesType(value, operand.value_type) &&
      (!Array.isArray(operand.allowed_values) || operand.allowed_values.includes(value));
  }

  function validCondition(condition, catalog) {
    if (!record(condition) || !CONDITION_OPERATORS.has(condition.operator)) return false;
    const operand = catalog[condition.operand];
    if (!record(operand) || !Object.prototype.hasOwnProperty.call(condition, "value")) return false;
    const values = condition.operator === "in" ? condition.value : [condition.value];
    if (!Array.isArray(values) || values.length === 0 || !values.every(function (value) { return valueMatchesOperand(value, operand); })) return false;
    return ["equals", "not_equals", "in"].includes(condition.operator) || ["number", "money", "date"].includes(operand.value_type);
  }

  function selectBundle(payload) {
    if (!record(payload) || payload.schema_version !== 1 || !Number.isInteger(payload.tax_year) || !record(payload.operand_catalog) || !record(payload.jurisdictions)) {
      return { valid: false };
    }
    const payloadDate = parseDate(payload.checked_on);
    if (!payloadDate) return { valid: false };
    const jurisdictionKeys = Object.keys(payload.jurisdictions);
    const jurisdictionId = typeof payload.active_jurisdiction_id === "string"
      ? payload.active_jurisdiction_id
      : jurisdictionKeys.length === 1 ? jurisdictionKeys[0] : null;
    const jurisdiction = typeof jurisdictionId === "string" ? payload.jurisdictions[jurisdictionId] : null;
    if (!record(jurisdiction) || jurisdiction.id !== jurisdictionId || !Array.isArray(jurisdiction.rules)) return { valid: false };
    if (!SCOPES.has(jurisdiction.resident_scope) || jurisdiction.resident_scope === "conditional" ||
        !SCOPES.has(jurisdiction.nonresident_scope) || jurisdiction.nonresident_scope === "conditional") return { valid: false };

    if (!Array.isArray(payload.sources) || payload.sources.length === 0 || !payload.sources.every(function (source) { return validSource(source, payloadDate); })) return { valid: false };
    const knownSources = new Set(payload.sources.map(function (source) { return source.id; }));
    if (knownSources.size !== payload.sources.length) return { valid: false };
    const rulesById = {};
    for (const rule of jurisdiction.rules) {
      if (!validRuleAudit(rule, payload, payloadDate, knownSources) || rulesById[rule.id]) return { valid: false };
      rulesById[rule.id] = rule;
    }

    const logic = jurisdiction.residence_logic;
    if (!record(logic) || !["any", "all"].includes(logic.operation) || !Array.isArray(logic.rule_ids) || logic.rule_ids.length === 0) return { valid: false };
    for (const ruleId of logic.rule_ids) {
      const rule = rulesById[ruleId];
      if (!record(rule) || rule.type !== "residence_test" || rule.category !== "tax_residence" || typeof rule.resident_when !== "boolean" ||
          !validFormula(rule.formula, payload.operand_catalog, FORMULA_OPERATIONS)) return { valid: false };
      if (rule.formula.operands.some(function (operandId) {
        const operand = payload.operand_catalog[operandId];
        return operand.kind === "profile" && operand.value_type === "string" && !Array.isArray(operand.allowed_values);
      })) return { valid: false };
    }

    const treatyRules = jurisdiction.rules.filter(function (rule) { return rule.branch_kind === "treaty_tie_breaker"; });
    const splitRules = jurisdiction.rules.filter(function (rule) { return rule.branch_kind === "split_year"; });
    if (treatyRules.length > 1 || splitRules.length > 1) return { valid: false };
    if (treatyRules.length === 1) {
      const treaty = treatyRules[0];
      if (treaty.type !== "branch" || treaty.category !== "tax_residence" || !record(treaty.formula) || treaty.formula.operation !== "conditional" ||
          !Array.isArray(treaty.formula.operands) || treaty.formula.operands.length === 0 || !Array.isArray(treaty.branches) || treaty.branches.length === 0 ||
          !treaty.formula.operands.every(function (operandId) { return validActiveOperand(payload.operand_catalog[operandId]); }) ||
          !treaty.branches.every(function (branch) {
            return record(branch) && validCondition(branch.when, payload.operand_catalog) && ["home", "destination"].includes(branch.residence_decision) && treaty.formula.operands.includes(branch.when.operand);
          })) return { valid: false };
    }
    if (splitRules.length === 1) {
      const split = splitRules[0];
      const dateOperand = payload.operand_catalog[split.date_operand];
      const activationOperand = payload.operand_catalog[split.activation_operand];
      if (split.type !== "branch" || split.category !== "tax_residence" || !record(split.formula) || split.formula.operation !== "conditional" ||
          !Array.isArray(split.formula.operands) || !split.formula.operands.includes(split.date_operand) || !split.formula.operands.includes(split.activation_operand) ||
          !record(dateOperand) || dateOperand.kind !== "profile" || dateOperand.value_type !== "date" ||
          !record(activationOperand) || activationOperand.kind !== "profile" || activationOperand.value_type !== "boolean" ||
          !Array.isArray(split.applies_to_statuses) || split.applies_to_statuses.length === 0 || !split.applies_to_statuses.every(function (status) { return STATUSES.has(status) && status !== "conditional"; }) ||
          !Array.isArray(split.periods) || split.periods.length !== 2) return { valid: false };
      const positions = new Set();
      for (const period of split.periods) {
        if (!record(period) || !["before", "from"].includes(period.position) || positions.has(period.position) || !STATUSES.has(period.status) || !scopesMatchStatus(period.status, period.scopes)) return { valid: false };
        positions.add(period.position);
      }
      if (!positions.has("before") || !positions.has("from")) return { valid: false };
    }
    return {
      valid: true,
      payload: payload,
      jurisdiction: jurisdiction,
      catalog: payload.operand_catalog,
      rulesById: rulesById,
      residenceRules: logic.rule_ids.map(function (id) { return rulesById[id]; }),
      logic: logic.operation,
      treaty: treatyRules[0] || null,
      split: splitRules[0] || null,
    };
  }

  function unknown(fact, invalid) {
    return { known: false, value: null, facts: fact ? [fact] : [], invalid: invalid === true };
  }

  function readOperand(profile, bundle, operandId, stack) {
    const operand = bundle.catalog[operandId];
    if (!record(operand)) return unknown(null, true);
    if (operand.kind === "constant") {
      return { known: true, value: operand.value, facts: [], invalid: false };
    }
    if (operand.kind === "derived") {
      if (stack.has(operandId)) return unknown(null, true);
      const next = new Set(stack);
      next.add(operandId);
      return evaluateFormula(profile, bundle, operand.derivation, next);
    }
    if (operand.kind !== "profile" || typeof operand.profile_key !== "string") return unknown(null, true);
    const fact = operand.profile_key;
    if (!Object.prototype.hasOwnProperty.call(profile, fact) || profile[fact] === null || profile[fact] === undefined || profile[fact] === "" || profile[fact] === "unknown") return unknown(fact, false);
    let value = profile[fact];
    if (operand.value_type === "number" || operand.value_type === "money") {
      if (typeof value !== "number" || !Number.isFinite(value)) return unknown(fact, false);
      if (typeof operand.minimum === "number" && value < operand.minimum) return unknown(fact, false);
      if (typeof operand.maximum === "number" && value > operand.maximum) return unknown(fact, false);
      if (operand.integer === true && !Number.isInteger(value)) return unknown(fact, false);
      if (operand.day_count === true && value > daysInYear(bundle.payload.tax_year)) return unknown(fact, false);
    } else if (operand.value_type === "boolean") {
      if (typeof value !== "boolean") return unknown(fact, false);
    } else if (operand.value_type === "string") {
      if (typeof value !== "string") return unknown(fact, false);
      if (!Array.isArray(operand.allowed_values) || !operand.allowed_values.includes(value)) return unknown(fact, false);
    } else if (operand.value_type === "date") {
      if (parseDate(value) === null) return unknown(fact, false);
    } else {
      return unknown(fact, true);
    }
    return { known: true, value: value, facts: [], invalid: false };
  }

  function evaluateFormula(profile, bundle, formula, stack) {
    if (!validFormula(formula, bundle.catalog, FORMULA_OPERATIONS)) return unknown(null, true);
    const operands = formula.operands.map(function (operandId) { return readOperand(profile, bundle, operandId, stack || new Set()); });
    const facts = unique(operands.flatMap(function (operand) { return operand.facts; }));
    if (operands.some(function (operand) { return operand.invalid; })) return { known: false, value: null, facts: facts, invalid: true };
    if (operands.some(function (operand) { return !operand.known; })) return { known: false, value: null, facts: facts, invalid: false };
    const left = operands[0].value;
    const right = operands.length > 1 ? operands[1].value : null;
    let value;
    if (formula.operation === "greater_than") value = left > right;
    else if (formula.operation === "greater_than_or_equal") value = left >= right;
    else if (formula.operation === "less_than") value = left < right;
    else if (formula.operation === "less_than_or_equal") value = left <= right;
    else if (formula.operation === "equals") value = left === right;
    else if (formula.operation === "not_equals") value = left !== right;
    else if (formula.operation === "flag" && typeof left === "boolean") value = left;
    else return unknown(null, true);
    return { known: true, value: value, facts: [], invalid: false };
  }

  function evaluateJurisdiction(profile, bundle, side) {
    const evaluations = [];
    for (const rule of bundle.residenceRules) {
      const formula = evaluateFormula(profile, bundle, rule.formula, new Set());
      if (formula.invalid) return { invalid: true };
      evaluations.push({ rule: rule, formula: formula, resident: formula.known ? formula.value === rule.resident_when : null });
    }
    const known = evaluations.filter(function (item) { return item.resident !== null; });
    const unknownItems = evaluations.filter(function (item) { return item.resident === null; });
    let resident;
    if (bundle.logic === "any") resident = known.some(function (item) { return item.resident; }) ? true : unknownItems.length ? null : false;
    else resident = known.some(function (item) { return !item.resident; }) ? false : unknownItems.length ? null : true;
    const materialUnknown = resident === null ? unknownItems : [];
    return {
      invalid: false,
      resident: resident,
      unresolvedFacts: unique(materialUnknown.flatMap(function (item) { return item.formula.facts; })),
      ruleIds: bundle.residenceRules.map(function (rule) { return rule.id; }),
      sourceIds: unique(bundle.residenceRules.flatMap(sourceIds)),
      explanations: evaluations.map(function (item) {
        return {
          code: item.rule.id,
          message: item.rule.explanation + (item.resident === true ? " This test indicates domestic residence." : item.resident === false ? " This test does not indicate domestic residence." : " A controlling profile value is unresolved."),
          ruleIds: [item.rule.id],
          sourceIds: sourceIds(item.rule),
        };
      }),
      side: side,
    };
  }

  function scopesFor(status, destination, home) {
    if (status === "likely_destination_resident") return { destination: destination.jurisdiction.resident_scope, home: home.jurisdiction.nonresident_scope };
    if (status === "likely_home_resident") return { destination: destination.jurisdiction.nonresident_scope, home: home.jurisdiction.resident_scope };
    if (status === "possible_dual_resident") return { destination: destination.jurisdiction.resident_scope, home: home.jurisdiction.resident_scope };
    return { destination: "conditional", home: "conditional" };
  }

  function evaluateCondition(profile, bundle, condition) {
    if (!validCondition(condition, bundle.catalog)) return unknown(null, true);
    const operand = readOperand(profile, bundle, condition.operand, new Set());
    if (!operand.known) return operand;
    const left = operand.value;
    const right = condition.value;
    let value;
    if (condition.operator === "equals") value = left === right;
    else if (condition.operator === "not_equals") value = left !== right;
    else if (condition.operator === "greater_than") value = left > right;
    else if (condition.operator === "greater_than_or_equal") value = left >= right;
    else if (condition.operator === "less_than") value = left < right;
    else if (condition.operator === "less_than_or_equal") value = left <= right;
    else if (condition.operator === "in") value = right.indexOf(left) !== -1;
    else return unknown(null, true);
    return { known: true, value: value, facts: [], invalid: false };
  }

  function treatyDecision(profile, bundle) {
    if (!bundle.treaty) return { decision: null, facts: [], invalid: false, absent: true };
    for (const branch of bundle.treaty.branches) {
      const condition = evaluateCondition(profile, bundle, branch.when);
      if (condition.invalid) return { decision: null, facts: [], invalid: true, absent: false };
      if (!condition.known) return { decision: null, facts: condition.facts, invalid: false, absent: false };
      if (condition.value) return { decision: branch.residence_decision, facts: [], invalid: false, absent: false };
    }
    return { decision: null, facts: [], invalid: false, absent: false };
  }

  function statusForKnown(profile, destinationResident, homeResident, destination, home) {
    if (destinationResident && !homeResident) return { statuses: ["likely_destination_resident"], treaty: null };
    if (!destinationResident && homeResident) return { statuses: ["likely_home_resident"], treaty: null };
    if (!destinationResident && !homeResident) return { statuses: ["conditional"], treaty: null };
    const treaty = treatyDecision(profile, destination);
    if (treaty.invalid) return { invalid: true, statuses: [] };
    if (treaty.absent || (!treaty.decision && treaty.facts.length === 0)) return { statuses: ["possible_dual_resident"], treaty: treaty };
    if (treaty.decision === "destination") return { statuses: ["likely_destination_resident"], treaty: treaty };
    if (treaty.decision === "home") return { statuses: ["likely_home_resident"], treaty: treaty };
    return { statuses: ["likely_home_resident", "likely_destination_resident", "possible_dual_resident"], treaty: treaty };
  }

  function possibleBranches(profile, destinationResident, homeResident, destination, home) {
    const destinationValues = destinationResident === null ? [false, true] : [destinationResident];
    const homeValues = homeResident === null ? [false, true] : [homeResident];
    const statuses = [];
    for (const destinationValue of destinationValues) {
      for (const homeValue of homeValues) {
        const outcome = statusForKnown(profile, destinationValue, homeValue, destination, home);
        if (outcome.invalid) return [];
        statuses.push.apply(statuses, outcome.statuses);
      }
    }
    return unique(statuses).map(function (status) { return { status: status, scopes: scopesFor(status, destination, home) }; });
  }

  function fullYear(year, status, scopes) {
    return [{ start: year + "-01-01", end: year + "-12-31", status: status, scopes: Object.assign({}, scopes) }];
  }

  function unavailable(facts) {
    return {
      status: "conditional",
      availability: "unavailable",
      taxYear: null,
      domesticResidence: { destination: null, home: null },
      treatyResidence: null,
      periods: [],
      scopes: { destination: "conditional", home: "conditional" },
      unresolvedFacts: unique(facts || ["residenceRules"]),
      materialFacts: unique(facts || ["residenceRules"]),
      branches: [],
      explanations: [{ code: "residence_rules_unavailable", message: "Validated residence rules are unavailable or malformed.", ruleIds: [], sourceIds: [] }],
      ruleIds: [],
      sourceIds: [],
    };
  }

  function evaluateResidence(profile, destinationRules, homeRules) {
    const destination = selectBundle(destinationRules);
    const home = selectBundle(homeRules);
    if (!record(profile) || !destination.valid || !home.valid || destination.payload.tax_year !== home.payload.tax_year) return unavailable(["residenceRules"]);
    const taxYear = destination.payload.tax_year;
    if (Object.prototype.hasOwnProperty.call(profile, "taxYear") && profile.taxYear !== taxYear) return unavailable(["taxYear"]);
    const destinationResult = evaluateJurisdiction(profile, destination, "destination");
    const homeResult = evaluateJurisdiction(profile, home, "home");
    if (destinationResult.invalid || homeResult.invalid) return unavailable(["residenceRules"]);

    let status = "conditional";
    let treatyResidence = null;
    let treaty = null;
    let unresolvedFacts = destinationResult.unresolvedFacts.concat(homeResult.unresolvedFacts);
    let ruleIds = destinationResult.ruleIds.concat(homeResult.ruleIds);
    let allSourceIds = destinationResult.sourceIds.concat(homeResult.sourceIds);
    let explanations = destinationResult.explanations.concat(homeResult.explanations);

    if (destinationResult.resident !== null && homeResult.resident !== null) {
      const outcome = statusForKnown(profile, destinationResult.resident, homeResult.resident, destination, home);
      if (outcome.invalid) return unavailable(["residenceRules"]);
      treaty = outcome.treaty;
      if (outcome.statuses.length === 1) status = outcome.statuses[0];
      if (treaty && treaty.facts.length) unresolvedFacts = unresolvedFacts.concat(treaty.facts);
      if (treaty && treaty.decision) treatyResidence = treaty.decision;
      if (treaty && !treaty.absent) {
        ruleIds.push(destination.treaty.id);
        allSourceIds = allSourceIds.concat(sourceIds(destination.treaty));
        explanations.push({ code: destination.treaty.id, message: destination.treaty.explanation, ruleIds: [destination.treaty.id], sourceIds: sourceIds(destination.treaty) });
      }
    }

    let scopes = scopesFor(status, destination, home);
    let periods = fullYear(taxYear, status, scopes);
    if (destination.split && destination.split.applies_to_statuses.includes(status)) {
      ruleIds.push(destination.split.id);
      allSourceIds = allSourceIds.concat(sourceIds(destination.split));
      explanations.push({ code: destination.split.id, message: destination.split.explanation, ruleIds: [destination.split.id], sourceIds: sourceIds(destination.split) });
      const activation = readOperand(profile, destination, destination.split.activation_operand, new Set());
      if (activation.invalid) return unavailable(["residenceRules"]);
      if (!activation.known) {
        status = "conditional";
        unresolvedFacts = unresolvedFacts.concat(activation.facts);
        scopes = scopesFor(status, destination, home);
        periods = fullYear(taxYear, status, scopes);
      } else if (activation.value === true) {
        const move = readOperand(profile, destination, destination.split.date_operand, new Set());
        const parsed = move.known ? parseDate(move.value) : null;
        if (move.invalid) return unavailable(["residenceRules"]);
        if (!move.known || parsed === null || parsed.year !== taxYear) {
          status = "conditional";
          unresolvedFacts = unresolvedFacts.concat(move.facts.length ? move.facts : [destination.catalog[destination.split.date_operand].profile_key]);
          scopes = scopesFor(status, destination, home);
          periods = fullYear(taxYear, status, scopes);
        } else {
          const before = destination.split.periods.find(function (period) { return period.position === "before"; });
          const from = destination.split.periods.find(function (period) { return period.position === "from"; });
          periods = [];
          if (parsed.text !== taxYear + "-01-01") periods.push({ start: taxYear + "-01-01", end: new Date(parsed.time - 86400000).toISOString().slice(0, 10), status: before.status, scopes: Object.assign({}, before.scopes) });
          periods.push({ start: parsed.text, end: taxYear + "-12-31", status: from.status, scopes: Object.assign({}, from.scopes) });
        }
      }
    }

    unresolvedFacts = unique(unresolvedFacts);
    const branches = status === "conditional" && unresolvedFacts.length > 0
      ? possibleBranches(profile, destinationResult.resident, homeResult.resident, destination, home)
      : [];
    return {
      status: status,
      availability: status === "conditional" ? "conditional" : "available",
      taxYear: taxYear,
      domesticResidence: { destination: destinationResult.resident, home: homeResult.resident },
      treatyResidence: treatyResidence,
      periods: periods,
      scopes: scopes,
      unresolvedFacts: unresolvedFacts,
      materialFacts: unresolvedFacts.slice(),
      branches: branches,
      explanations: explanations,
      ruleIds: unique(ruleIds),
      sourceIds: unique(allSourceIds),
    };
  }

  return { evaluateResidence: evaluateResidence };
});
