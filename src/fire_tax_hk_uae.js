(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxHongKongUAE = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  function record(value) { return value !== null && typeof value === "object" && !Array.isArray(value); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }

  function selectedSources(sourceIds, sources) {
    const byId = Object.fromEntries((sources || []).map(function (source) { return [source.id, source]; }));
    return (sourceIds || []).map(function (id) {
      if (!record(byId[id])) throw new TypeError("Validated runtime source is missing: " + id);
      return clone(byId[id]);
    });
  }

  function ruleMetadata(rule, graph, currency) {
    return Object.assign({}, clone(rule), {
      tax_year: graph.tax_year,
      currency: currency,
      effective_from: graph.effective_from,
      checked_on: graph.checked_on,
      review_interval_days: graph.review_interval_days,
      confidence: "high",
      recheck_trigger: graph.recheck_trigger,
    });
  }

  function residenceBundle(item, graph, currency, sources, side) {
    const rules = item.rules.map(function (rule) { return ruleMetadata(rule, graph, currency); });
    return {
      schema_version: graph.schema_version,
      tax_year: graph.tax_year,
      checked_on: graph.checked_on,
      operand_catalog: clone(item.operands),
      sources: selectedSources(item.source_ids, sources),
      active_jurisdiction_id: item.jurisdiction_id,
      jurisdictions: { [item.jurisdiction_id]: {
        id: item.jurisdiction_id,
        label: item.label,
        synthetic: false,
        detailed_enabled: true,
        calculation_side: side,
        resident_scope: "worldwide_income",
        nonresident_scope: "source_income",
        residence_logic: { operation: "any", rule_ids: rules.map(function (rule) { return rule.id; }) },
        rules: rules,
      } },
    };
  }

  function incomeBundle(item, graph, currency, sources) {
    const catalog = {};
    const rules = item.categories.map(function (category) {
      const operandId = item.formula.operand_prefix + category;
      catalog[operandId] = { kind: "profile", profile_key: item.profile_keys[category], value_type: "money", currency: currency };
      const rule = ruleMetadata({
        id: item.rule_ids[category],
        type: "rate_band",
        taxpayer_scope: ["resident", "nonresident"],
        category: category,
        source_ids: item.source_ids,
        formula: { operation: item.formula.operation, operands: [operandId] },
        bands: clone(item.bands),
        no_tax: item.no_tax,
        explanation: item.explanation,
      }, graph, currency);
      if (category === "retirement_account_withdrawal") {
        catalog.retirement_classification = { kind: "profile", profile_key: "retirementAccountClassification", value_type: "string", allowed_values: ["personal_investment"] };
        rule.account_classification_operand = "retirement_classification";
        rule.supported_account_classifications = ["personal_investment"];
      }
      return rule;
    });
    return {
      schema_version: graph.schema_version,
      tax_year: graph.tax_year,
      checked_on: graph.checked_on,
      operand_catalog: catalog,
      sources: selectedSources(item.source_ids, sources),
      active_jurisdiction_id: item.jurisdiction_id,
      jurisdictions: { [item.jurisdiction_id]: {
        id: item.jurisdiction_id,
        label: item.label,
        synthetic: false,
        detailed_enabled: true,
        calculation_side: item.calculation_side,
        resident_scope: "worldwide_income",
        nonresident_scope: "source_income",
        rules: rules,
      } },
    };
  }

  function propertyBundle(item, graph) {
    return {
      schema_version: graph.schema_version,
      tax_year: graph.tax_year,
      checked_on: graph.checked_on,
      operand_catalog: {},
      sources: [],
      active_jurisdiction_id: item.jurisdiction_id,
      jurisdictions: { [item.jurisdiction_id]: {
        id: item.jurisdiction_id,
        label: item.label,
        synthetic: false,
        detailed_enabled: true,
        calculation_side: item.calculation_side,
        resident_scope: "worldwide_income",
        nonresident_scope: "source_income",
        property_coverage: {},
        rules: [],
      } },
    };
  }

  function buildRuntimeBundle(definition, profile, sources) {
    if (!record(definition) || !record(profile) || definition.runtime_definition.factory !== "hong-kong-to-dubai-v1") throw new TypeError("Unsupported detailed profile factory");
    if (!record(definition.runtime_rule_graph) || definition.runtime_rule_graph.schema_version !== 1) throw new TypeError("A validated serialized runtime rule graph is required");
    if (!record(profile.destination) || !record(profile.destination.property) || profile.destination.property.enabled !== false) throw new TypeError("The enabled Hong Kong to Dubai exact graph is renter-only");
    const graph = definition.runtime_rule_graph;
    const currency = profile.destination.income.currency;
    const residence = {
      destination: residenceBundle(graph.residence.destination, graph, currency, sources, "destination"),
      home: residenceBundle(graph.residence.home, graph, currency, sources, "home"),
    };
    return {
      residence: residence,
      rules: {
        residence: residence,
        destination: {
          income: incomeBundle(graph.income.destination, graph, currency, sources),
          credits: clone(graph.credits.destination),
          property: propertyBundle(graph.property.destination, graph),
        },
        continuingHome: {
          income: incomeBundle(graph.income.continuing_home, graph, currency, sources),
          credits: clone(graph.credits.continuing_home),
          property: propertyBundle(graph.property.continuing_home, graph),
        },
      },
    };
  }

  return { buildRuntimeBundle: buildRuntimeBundle };
});
