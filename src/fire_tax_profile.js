(function (root, factory) {
  const residence = typeof module === "object" && module.exports
    ? require("./fire_tax_residence.js")
    : root && root.GHAFireTaxResidence;
  const api = factory(residence);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxProfile = api;
})(typeof window !== "undefined" ? window : null, function (residence) {
  "use strict";

  const CONTROLS = new Set(["number", "select", "radio", "date", "checkbox"]);

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function parseDate(value) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const parts = value.split("-").map(Number);
    const date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    return date.getUTCFullYear() === parts[0] && date.getUTCMonth() === parts[1] - 1 && date.getUTCDate() === parts[2]
      ? { year: parts[0], text: value }
      : null;
  }

  function activeJurisdiction(payload) {
    if (!record(payload) || !record(payload.operand_catalog) || !record(payload.jurisdictions) || typeof payload.active_jurisdiction_id !== "string") return null;
    const jurisdiction = payload.jurisdictions[payload.active_jurisdiction_id];
    return record(jurisdiction) ? jurisdiction : null;
  }

  function ruleUsesOperand(rule, operandId) {
    if (!record(rule)) return false;
    if (record(rule.formula) && Array.isArray(rule.formula.operands) && rule.formula.operands.includes(operandId)) return true;
    if (rule.date_operand === operandId || rule.activation_operand === operandId) return true;
    return Array.isArray(rule.branches) && rule.branches.some(function (branch) {
      return record(branch) && record(branch.when) && branch.when.operand === operandId;
    });
  }

  function valueMatches(value, operand) {
    if (value === "unknown") return true;
    if (operand.value_type === "number") {
      return typeof value === "number" && Number.isFinite(value) &&
        (typeof operand.minimum !== "number" || value >= operand.minimum) &&
        (typeof operand.maximum !== "number" || value <= operand.maximum) &&
        (operand.integer !== true || Number.isInteger(value));
    }
    if (operand.value_type === "boolean") return typeof value === "boolean";
    if (operand.value_type === "string") return typeof value === "string" && value.length > 0 && (!Array.isArray(operand.allowed_values) || operand.allowed_values.includes(value));
    if (operand.value_type === "date") return parseDate(value) !== null;
    return false;
  }

  function validAccepted(question, operand, taxYear) {
    const accepted = question.accepted_values;
    if (question.control === "number") {
      return record(accepted) && typeof accepted.min === "number" && typeof accepted.max === "number" && typeof accepted.step === "number" && accepted.step > 0 && accepted.min <= accepted.max && typeof accepted.integer === "boolean" && operand.value_type === "number" &&
        valueMatches(accepted.min, operand) && valueMatches(accepted.max, operand) &&
        (operand.integer !== true || accepted.integer === true) && (accepted.integer !== true || Number.isInteger(accepted.step));
    }
    if (question.control === "date") {
      const minimum = record(accepted) ? parseDate(accepted.min) : null;
      const maximum = record(accepted) ? parseDate(accepted.max) : null;
      return minimum !== null && maximum !== null && accepted.min <= accepted.max && minimum.year === taxYear && maximum.year === taxYear && operand.value_type === "date";
    }
    if (question.control === "checkbox") {
      return Array.isArray(accepted) && accepted.length === 2 && accepted.includes(true) && accepted.includes(false) && operand.value_type === "boolean";
    }
    return Array.isArray(accepted) && accepted.length >= 2 && accepted.every(function (value) { return valueMatches(value, operand); });
  }

  function valueIsAccepted(value, control, accepted) {
    if (control === "number") return typeof value === "number" && value >= accepted.min && value <= accepted.max && (accepted.integer !== true || Number.isInteger(value));
    if (control === "date") return typeof value === "string" && value >= accepted.min && value <= accepted.max;
    return Array.isArray(accepted) && accepted.some(function (candidate) { return candidate === value; });
  }

  function normalizedQuestions(payload) {
    const jurisdiction = activeJurisdiction(payload);
    if (!jurisdiction || !Array.isArray(jurisdiction.questions) || !Array.isArray(jurisdiction.rules)) return [];
    const rulesById = {};
    jurisdiction.rules.forEach(function (rule) {
      if (record(rule) && typeof rule.id === "string") rulesById[rule.id] = rule;
    });
    const activeRuleIds = new Set(
      (record(jurisdiction.residence_logic) && Array.isArray(jurisdiction.residence_logic.rule_ids)
        ? jurisdiction.residence_logic.rule_ids
        : []).concat(
        jurisdiction.rules.filter(function (rule) { return record(rule) && ["treaty_tie_breaker", "split_year"].includes(rule.branch_kind); }).map(function (rule) { return rule.id; })
      )
    );
    return jurisdiction.questions.reduce(function (result, question) {
      if (!record(question) || typeof question.id !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(question.id) ||
          typeof question.operand_id !== "string" || !CONTROLS.has(question.control) || typeof question.label !== "string" || !question.label.trim() ||
          /[<>]/.test(question.label) || typeof question.reason !== "string" || !question.reason.trim() || /[<>]/.test(question.reason)) return result;
      const operand = payload.operand_catalog[question.operand_id];
      if (!record(operand) || operand.kind !== "profile" || typeof operand.profile_key !== "string" || !validAccepted(question, operand, payload.tax_year) ||
          !Array.isArray(question.materiality_values) || question.materiality_values.length < 2 ||
          !question.materiality_values.every(function (value) { return valueMatches(value, operand); }) ||
          (question.control === "date" && !question.materiality_values.every(function (value) { const parsed = parseDate(value); return parsed !== null && parsed.year === payload.tax_year; })) ||
          !question.materiality_values.every(function (value) { return valueIsAccepted(value, question.control, question.accepted_values); }) ||
          new Set(question.materiality_values.map(JSON.stringify)).size < 2 ||
          !Array.isArray(question.affects_rule_ids) || question.affects_rule_ids.length === 0 ||
          !question.affects_rule_ids.every(function (ruleId) { return activeRuleIds.has(ruleId) && ruleUsesOperand(rulesById[ruleId], question.operand_id); })) return result;
      result.push({
        id: question.id,
        operandId: question.operand_id,
        fact: operand.profile_key,
        control: question.control,
        label: question.label.trim(),
        reason: question.reason.trim(),
        acceptedValues: Array.isArray(question.accepted_values) ? question.accepted_values.slice() : Object.assign({}, question.accepted_values),
        materialityValues: question.materiality_values.slice(),
        affectsRuleIds: question.affects_rule_ids.slice(),
        affectedRules: question.affects_rule_ids.map(function (ruleId) { return rulesById[ruleId]; }),
      });
      return result;
    }, []);
  }

  function mergeQuestions(destinationRules, homeRules) {
    const merged = new Map();
    normalizedQuestions(destinationRules).concat(normalizedQuestions(homeRules)).forEach(function (question) {
      const existing = merged.get(question.id);
      if (!existing) {
        merged.set(question.id, question);
        return;
      }
      const sameDescriptor = existing.fact === question.fact && existing.control === question.control && existing.label === question.label && existing.reason === question.reason && JSON.stringify(existing.acceptedValues) === JSON.stringify(question.acceptedValues) && JSON.stringify(existing.materialityValues) === JSON.stringify(question.materialityValues);
      if (!sameDescriptor) {
        merged.delete(question.id);
        return;
      }
      existing.affectsRuleIds = Array.from(new Set(existing.affectsRuleIds.concat(question.affectsRuleIds)));
      existing.affectedRules = existing.affectedRules.concat(question.affectedRules);
    });
    return Array.from(merged.values());
  }

  function signature(result) {
    if (!record(result) || result.availability === "unavailable") return null;
    return JSON.stringify({
      status: result.status,
      domesticResidence: result.domesticResidence,
      treatyResidence: result.treatyResidence,
      periods: result.periods,
      scopes: result.scopes,
      unresolvedFacts: result.unresolvedFacts,
      branches: result.branches,
    });
  }

  function profileKeyForOperand(operandId, rules) {
    for (const payload of [rules.destinationRules, rules.homeRules]) {
      const operand = record(payload) && record(payload.operand_catalog) ? payload.operand_catalog[operandId] : null;
      if (record(operand) && typeof operand.profile_key === "string") return operand.profile_key;
    }
    return null;
  }

  function ruleIsReached(rule, question, profile, currentResult, rules) {
    if (!record(rule)) return false;
    if (rule.branch_kind === "treaty_tie_breaker") {
      return record(currentResult.domesticResidence) &&
        currentResult.domesticResidence.destination === true &&
        currentResult.domesticResidence.home === true;
    }
    if (rule.branch_kind === "split_year") {
      const possibleStatuses = [currentResult.status].concat(
        Array.isArray(currentResult.branches) ? currentResult.branches.map(function (branch) { return branch.status; }) : []
      );
      if (!Array.isArray(rule.applies_to_statuses) || !rule.applies_to_statuses.some(function (status) { return possibleStatuses.includes(status); })) return false;
      if (question.operandId === rule.activation_operand) return true;
      if (question.operandId === rule.date_operand) {
        const activationFact = profileKeyForOperand(rule.activation_operand, rules);
        return activationFact !== null && profile[activationFact] === true;
      }
    }
    return true;
  }

  function nextQuestions(profile, rules, currentResult) {
    if (!record(profile) || !record(rules) || !record(currentResult) || !residence || typeof residence.evaluateResidence !== "function") return [];
    if (currentResult.availability === "unavailable" || !record(rules.destinationRules) || !record(rules.homeRules)) return [];
    return mergeQuestions(rules.destinationRules, rules.homeRules).reduce(function (result, question) {
      if (Object.prototype.hasOwnProperty.call(profile, question.fact) && valueIsAccepted(profile[question.fact], question.control, question.acceptedValues)) return result;
      if (!question.affectedRules.some(function (rule) { return ruleIsReached(rule, question, profile, currentResult, rules); })) return result;
      const outcomes = new Set();
      for (const value of question.materialityValues) {
        const candidate = Object.assign({}, profile);
        candidate[question.fact] = value;
        const candidateResult = residence.evaluateResidence(candidate, rules.destinationRules, rules.homeRules);
        const candidateSignature = signature(candidateResult);
        if (candidateSignature === null) return result;
        outcomes.add(candidateSignature);
      }
      if (outcomes.size < 2) return result;
      result.push({
        id: question.id,
        fact: question.fact,
        control: question.control,
        label: question.label,
        reason: question.reason,
        acceptedValues: question.acceptedValues,
        affectsRuleIds: question.affectsRuleIds,
      });
      return result;
    }, []);
  }

  return { nextQuestions: nextQuestions };
});
