(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxProfile = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const CONTROLS = new Set(["number", "select", "date", "radio", "checkbox"]);

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function answered(profile, fact) {
    if (!Object.prototype.hasOwnProperty.call(profile, fact)) return false;
    const value = profile[fact];
    return value !== undefined && value !== null && value !== "";
  }

  function distinctOutcomes(question) {
    if (!record(question.outcomes)) return true;
    const values = Object.values(question.outcomes).map(function (value) {
      try {
        return JSON.stringify(value);
      } catch (_error) {
        return String(value);
      }
    });
    return new Set(values).size > 1;
  }

  function validQuestion(question) {
    return record(question) &&
      typeof question.id === "string" && question.id.length > 0 &&
      typeof question.fact === "string" && question.fact.length > 0 &&
      CONTROLS.has(question.control) &&
      typeof question.label === "string" && question.label.trim().length > 0 &&
      typeof question.reason === "string" && question.reason.trim().length > 0 &&
      (Array.isArray(question.acceptedValues) || record(question.acceptedValues)) &&
      Array.isArray(question.affectsRuleIds) &&
      question.affectsRuleIds.some(function (id) { return typeof id === "string" && id.length > 0; });
  }

  function nextQuestions(profile, rules, currentResult) {
    if (!record(profile) || !record(rules) || !record(currentResult)) return [];
    if (!Array.isArray(rules.questions) || !Array.isArray(currentResult.materialFacts)) return [];

    const materialFacts = new Set(currentResult.materialFacts.filter(function (fact) {
      return typeof fact === "string";
    }));
    const activeRuleIds = new Set(
      Array.isArray(currentResult.ruleIds)
        ? currentResult.ruleIds.filter(function (id) { return typeof id === "string"; })
        : []
    );
    const seenIds = new Set();
    const seenFacts = new Set();

    return rules.questions.reduce(function (questions, question) {
      if (!validQuestion(question) || seenIds.has(question.id) || seenFacts.has(question.fact)) {
        return questions;
      }
      if (!materialFacts.has(question.fact) || answered(profile, question.fact)) return questions;
      if (!distinctOutcomes(question)) return questions;
      if (activeRuleIds.size > 0 && !question.affectsRuleIds.some(function (id) {
        return activeRuleIds.has(id);
      })) return questions;

      seenIds.add(question.id);
      seenFacts.add(question.fact);
      questions.push({
        id: question.id,
        fact: question.fact,
        control: question.control,
        label: question.label.trim(),
        reason: question.reason.trim(),
        acceptedValues: Array.isArray(question.acceptedValues)
          ? question.acceptedValues.slice()
          : Object.assign({}, question.acceptedValues),
        affectsRuleIds: question.affectsRuleIds.filter(function (id) {
          return typeof id === "string" && id.length > 0;
        }),
      });
      return questions;
    }, []);
  }

  return { nextQuestions: nextQuestions };
});
