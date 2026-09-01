(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxProperty = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const STAGES = ["purchase", "annual", "rental", "sale", "inheritance", "gift"];
  const STAGE_CATEGORIES = {
    purchase: "property_purchase",
    annual: "property_annual",
    rental: "property_rental",
    sale: "property_sale",
    inheritance: "property_inheritance",
    gift: "property_gift"
  };
  const CONFIDENCE = ["low", "medium", "medium_high", "high"];
  const SCOPES = new Set(["resident", "nonresident"]);
  const CONDITION_OPERATORS = new Set(["equals", "not_equals", "less_than", "less_than_or_equal", "greater_than", "greater_than_or_equal", "in"]);

  class FireTaxPropertyInputError extends Error {
    constructor(message) {
      super(message);
      this.name = "FireTaxPropertyInputError";
    }
  }

  class FireTaxPropertyRuleError extends Error {
    constructor(message) {
      super(message);
      this.name = "FireTaxPropertyRuleError";
    }
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function finite(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function round(value) {
    return Math.round((value + Number.EPSILON) * 100000000) / 100000000;
  }

  function unique(values) {
    return Array.from(new Set(values.filter(function (value) {
      return typeof value === "string" && value.length > 0;
    })));
  }

  function lowestConfidence(values) {
    return values.reduce(function (lowest, value) {
      return CONFIDENCE.indexOf(value) < CONFIDENCE.indexOf(lowest) ? value : lowest;
    }, "high");
  }

  function valueMatches(value, operand) {
    if (!record(operand)) return false;
    if (operand.value_type === "money") return finite(value) && value >= 0;
    if (operand.value_type === "number") {
      if (!finite(value)) return false;
      if (finite(operand.minimum) && value < operand.minimum) return false;
      if (finite(operand.maximum) && value > operand.maximum) return false;
      if (operand.integer === true && !Number.isInteger(value)) return false;
      return true;
    }
    if (operand.value_type === "string") {
      return typeof value === "string" && (!Array.isArray(operand.allowed_values) || operand.allowed_values.includes(value));
    }
    if (operand.value_type === "boolean") return typeof value === "boolean";
    return false;
  }

  function validateCondition(condition, bundle, path) {
    if (!record(condition) || typeof condition.operand !== "string" || !CONDITION_OPERATORS.has(condition.operator)) {
      throw new FireTaxPropertyRuleError(path + " is not an executable condition");
    }
    const operand = bundle.catalog[condition.operand];
    if (!record(operand) || operand.kind !== "profile") {
      throw new FireTaxPropertyRuleError(path + ".operand must reference a profile operand");
    }
    if (operand.profile_key === "heirRelationship" && (!Array.isArray(operand.allowed_values) || operand.allowed_values.length === 0 || new Set(operand.allowed_values).size !== operand.allowed_values.length)) {
      throw new FireTaxPropertyRuleError(path + ".operand must declare complete allowed relationship values");
    }
    const values = condition.operator === "in" ? condition.value : [condition.value];
    if (!Array.isArray(values) || values.length === 0 || !values.every(function (value) { return valueMatches(value, operand); })) {
      throw new FireTaxPropertyRuleError(path + ".value does not match the operand contract");
    }
  }

  function validateBands(rule) {
    if (!Array.isArray(rule.bands) || rule.bands.length === 0) return false;
    let from = 0;
    for (let index = 0; index < rule.bands.length; index += 1) {
      const band = rule.bands[index];
      if (!record(band) || !finite(band.from) || band.from !== from || !finite(band.rate) || band.rate < 0 || band.rate > 1) return false;
      if (band.up_to === null) {
        if (index !== rule.bands.length - 1) return false;
        from = null;
      } else if (!finite(band.up_to) || band.up_to <= band.from) {
        return false;
      } else {
        from = band.up_to;
      }
    }
    return from === null;
  }

  function propertyOperandRoots(rules) {
    return unique(rules.flatMap(function (rule) {
      const roots = [];
      if (record(rule.formula) && Array.isArray(rule.formula.operands)) roots.push.apply(roots, rule.formula.operands);
      if (Array.isArray(rule.applies_when)) {
        roots.push.apply(roots, rule.applies_when.map(function (condition) {
          return record(condition) ? condition.operand : null;
        }));
      }
      if (record(rule.unknown_operand_range)) {
        roots.push(rule.unknown_operand_range.operand, rule.unknown_operand_range.reference_operand);
      }
      roots.push(rule.rate_operand, rule.amount_operand);
      return roots;
    }));
  }

  function validateCatalog(catalog, rootOperandIds) {
    if (!record(catalog) || Object.keys(catalog).length === 0) {
      throw new FireTaxPropertyRuleError("rules must include a validated operand catalog");
    }
    const visited = new Set();
    function visit(operandId) {
      if (visited.has(operandId)) return;
      visited.add(operandId);
      const operand = catalog[operandId];
      if (!record(operand) || !["profile", "constant", "derived"].includes(operand.kind) || !["money", "number", "string", "boolean"].includes(operand.value_type)) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " is not executable");
      }
      if (operand.value_type === "money" && (typeof operand.currency !== "string" || !/^[A-Z]{3}$/.test(operand.currency))) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " has invalid currency metadata");
      }
      if (operand.kind === "profile" && typeof operand.profile_key !== "string") {
        throw new FireTaxPropertyRuleError("operand " + operandId + " is missing its profile key");
      }
      if (operand.kind === "profile" && operand.profile_key === "heirRelationship" && (!Array.isArray(operand.allowed_values) || operand.allowed_values.length < 2 || !operand.allowed_values.every(function (value) { return typeof value === "string" && value.length > 0 && value !== "unknown"; }) || new Set(operand.allowed_values).size !== operand.allowed_values.length)) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " must declare complete allowed relationship values");
      }
      if (operand.kind === "constant" && !valueMatches(operand.value, operand)) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " has an invalid constant value");
      }
      if (operand.audit_role !== undefined && (operand.audit_role !== "allowance" || operand.kind !== "constant" || operand.value_type !== "money" || !finite(operand.value) || operand.value < 0)) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " has an invalid audit role");
      }
      if (operand.kind === "derived" && (!record(operand.derivation) || !["add", "subtract", "multiply", "minimum", "maximum"].includes(operand.derivation.operation) || !Array.isArray(operand.derivation.operands) || operand.derivation.operands.length < 2)) {
        throw new FireTaxPropertyRuleError("operand " + operandId + " has an invalid derivation");
      }
      if (operand.kind === "derived") operand.derivation.operands.forEach(visit);
    }
    rootOperandIds.forEach(visit);
  }

  function selectBundle(payload) {
    if (!record(payload) || payload.schema_version !== 1 || !Number.isInteger(payload.tax_year) || !record(payload.jurisdictions)) {
      throw new FireTaxPropertyRuleError("rules must be a validated Task 1 rule payload");
    }
    const jurisdictionIds = Object.keys(payload.jurisdictions);
    const jurisdictionId = typeof payload.active_jurisdiction_id === "string"
      ? payload.active_jurisdiction_id
      : jurisdictionIds.length === 1 ? jurisdictionIds[0] : null;
    const jurisdiction = jurisdictionId ? payload.jurisdictions[jurisdictionId] : null;
    if (!record(jurisdiction) || jurisdiction.id !== jurisdictionId || !Array.isArray(jurisdiction.rules)) {
      throw new FireTaxPropertyRuleError("active jurisdiction must identify a validated rule graph");
    }
    if (jurisdiction.calculation_side !== "destination" && jurisdiction.calculation_side !== "home") {
      throw new FireTaxPropertyRuleError("jurisdiction calculation_side must be destination or home");
    }
    if (!Array.isArray(payload.sources) || payload.sources.length === 0) {
      throw new FireTaxPropertyRuleError("rules must include source audit records");
    }
    const sourceIds = new Set();
    payload.sources.forEach(function (source, index) {
      if (!record(source) || typeof source.id !== "string" || sourceIds.has(source.id) || typeof source.url !== "string" || typeof source.checked_on !== "string") {
        throw new FireTaxPropertyRuleError("source record " + index + " is invalid or duplicated");
      }
      sourceIds.add(source.id);
    });
    const bundle = {
      payload: payload,
      catalog: payload.operand_catalog,
      jurisdiction: jurisdiction,
      jurisdictionId: jurisdictionId,
      side: jurisdiction.calculation_side,
      sourceIds: sourceIds
    };
    const seen = new Set();
    const rules = jurisdiction.rules.filter(function (rule) { return record(rule) && rule.type === "property_charge"; });
    if (rules.length === 0) throw new FireTaxPropertyRuleError("active jurisdiction has no validated property charges");
    validateCatalog(payload.operand_catalog, propertyOperandRoots(rules));
    rules.forEach(function (rule, index) {
      const path = "property rule " + index;
      if (typeof rule.id !== "string" || !rule.id.endsWith("-" + payload.tax_year) || seen.has(rule.id)) {
        throw new FireTaxPropertyRuleError(path + " has an invalid or duplicate rule ID");
      }
      seen.add(rule.id);
      if (rule.tax_year !== payload.tax_year || !Array.isArray(rule.taxpayer_scope) || rule.taxpayer_scope.length === 0 || !rule.taxpayer_scope.every(function (scope) { return SCOPES.has(scope); })) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has invalid tax year or taxpayer scope");
      }
      if (!STAGES.includes(rule.lifecycle_stage) || rule.category !== STAGE_CATEGORIES[rule.lifecycle_stage]) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid lifecycle category");
      }
      if (typeof rule.currency !== "string" || !/^[A-Z]{3}$/.test(rule.currency) || typeof rule.charge_kind !== "string" || !["tax", "non_tax"].includes(rule.tax_or_non_tax) || !["current_liability", "prepayment"].includes(rule.payment_treatment)) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has incomplete classification metadata");
      }
      if (rule.payment_treatment === "prepayment" && rule.tax_or_non_tax !== "tax") {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " cannot classify a non-tax cost as a prepayment");
      }
      if (!Array.isArray(rule.source_ids) || rule.source_ids.length === 0 || !rule.source_ids.every(function (sourceId) { return sourceIds.has(sourceId); })) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has invalid source IDs");
      }
      if (!CONFIDENCE.includes(rule.confidence) || typeof rule.explanation !== "string" || rule.explanation.trim().length === 0 || typeof rule.effective_from !== "string" || typeof rule.checked_on !== "string") {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has incomplete audit metadata");
      }
      if (!record(rule.formula) || !["add", "multiply", "progressive_rate"].includes(rule.formula.operation) || !Array.isArray(rule.formula.operands) || rule.formula.operands.length === 0 || !rule.formula.operands.every(function (id) { return record(bundle.catalog[id]); })) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid formula");
      }
      if (rule.formula.operation === "multiply" && (!finite(rule.rate) || rule.rate < 0 || rule.rate > 1 || rule.formula.operands[1] !== rule.rate_operand || !record(bundle.catalog[rule.rate_operand]) || bundle.catalog[rule.rate_operand].value !== rule.rate)) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid linked rate");
      }
      if (rule.formula.operation === "add" && (!finite(rule.amount) || rule.amount < 0 || !rule.formula.operands.includes(rule.amount_operand) || !record(bundle.catalog[rule.amount_operand]) || bundle.catalog[rule.amount_operand].value !== rule.amount)) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid linked fixed amount");
      }
      if (rule.formula.operation === "progressive_rate" && !validateBands(rule)) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has invalid progressive bands");
      }
      if (Object.prototype.hasOwnProperty.call(rule, "floor_at_zero") && typeof rule.floor_at_zero !== "boolean") {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid floor_at_zero marker");
      }
      if (Object.prototype.hasOwnProperty.call(rule, "allowance_amount")) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " allowance audit must derive from formula operands");
      }
      if (rule.applies_when !== undefined && (!Array.isArray(rule.applies_when) || rule.applies_when.length === 0)) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + ".applies_when must contain executable conditions");
      }
      (rule.applies_when || []).forEach(function (condition, conditionIndex) {
        validateCondition(condition, bundle, "property rule " + rule.id + ".applies_when[" + conditionIndex + "]");
      });
      if (rule.unknown_operand_range !== undefined) {
        const range = rule.unknown_operand_range;
        const operand = record(range) ? bundle.catalog[range.operand] : null;
        const reference = record(range) ? bundle.catalog[range.reference_operand] : null;
        if (!record(range) || !record(operand) || operand.kind !== "profile" || operand.value_type !== "money" || !record(reference) || reference.kind !== "profile" || reference.value_type !== "money" || !finite(range.minimum_ratio) || !finite(range.maximum_ratio) || range.minimum_ratio < 0 || range.maximum_ratio < range.minimum_ratio || range.maximum_ratio > 1) {
          throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid unknown-operand range");
        }
      }
      if (rule.retirement_cost_boundary !== undefined && (rule.retirement_cost_boundary !== "owner_property_tax" || rule.lifecycle_stage !== "annual" || rule.tax_or_non_tax !== "tax" || rule.payment_treatment !== "current_liability")) {
        throw new FireTaxPropertyRuleError("property rule " + rule.id + " has an invalid retirement cost boundary");
      }
    });
    const coverage = jurisdiction.property_coverage;
    if (!record(coverage) || Object.keys(coverage).length !== STAGES.length || !STAGES.every(function (stage) { return Object.prototype.hasOwnProperty.call(coverage, stage); })) {
      throw new FireTaxPropertyRuleError("property coverage must declare every lifecycle stage");
    }
    bundle.coverageRules = {};
    STAGES.forEach(function (stage) {
      if (!record(coverage[stage])) throw new FireTaxPropertyRuleError("property coverage " + stage + " must declare resident and nonresident scopes");
      bundle.coverageRules[stage] = {};
      ["resident", "nonresident"].forEach(function (scope) {
        const entry = coverage[stage][scope];
        const path = stage + "." + scope;
        if (!record(entry) || !["supported", "no_tax"].includes(entry.treatment) || !Array.isArray(entry.rule_ids) || entry.rule_ids.length === 0 || new Set(entry.rule_ids).size !== entry.rule_ids.length) {
          throw new FireTaxPropertyRuleError("property coverage " + path + " is missing or invalid");
        }
        const expected = rules.filter(function (rule) {
          return rule.lifecycle_stage === stage && rule.taxpayer_scope.includes(scope);
        });
        const expectedIds = expected.map(function (rule) { return rule.id; }).sort();
        const declaredIds = entry.rule_ids.slice().sort();
        if (expectedIds.length !== declaredIds.length || expectedIds.some(function (id, index) { return id !== declaredIds[index]; })) {
          throw new FireTaxPropertyRuleError("property coverage " + path + " must exactly include its applicable rules");
        }
        if (entry.treatment === "no_tax" && expected.some(function (rule) {
          if (rule.no_tax !== true) return true;
          if (rule.formula.operation === "multiply") return rule.rate !== 0;
          if (rule.formula.operation === "progressive_rate") return rule.bands.some(function (band) { return band.rate !== 0; });
          return true;
        })) {
          throw new FireTaxPropertyRuleError("property coverage " + path + " no_tax must use explicit executable zero-tax rules");
        }
        bundle.coverageRules[stage][scope] = expected;
      });
    });
    const relationshipOperandIds = unique(rules.flatMap(function (rule) {
      return (rule.applies_when || []).filter(function (condition) {
        const operand = bundle.catalog[condition.operand];
        return record(operand) && operand.profile_key === "heirRelationship";
      }).map(function (condition) { return condition.operand; });
    }));
    relationshipOperandIds.forEach(function (operandId) {
      const domain = bundle.catalog[operandId].allowed_values;
      STAGES.forEach(function (stage) {
        ["resident", "nonresident"].forEach(function (scope) {
          const scoped = bundle.coverageRules[stage][scope].filter(function (rule) {
            return (rule.applies_when || []).some(function (condition) { return condition.operand === operandId; });
          });
          if (scoped.length === 0) return;
          domain.forEach(function (value) {
            const covered = scoped.some(function (rule) {
              return (rule.applies_when || []).filter(function (condition) { return condition.operand === operandId; }).every(function (condition) {
                return compare(value, condition);
              });
            });
            if (!covered) throw new FireTaxPropertyRuleError("relationship allowed value " + value + " has no executable " + stage + "." + scope + " branch");
          });
        });
      });
    });
    bundle.rules = rules;
    return bundle;
  }

  function validateProfileHeader(profile, bundle) {
    if (!record(profile)) throw new FireTaxPropertyInputError("propertyProfile must be an object");
    if (profile.taxYear !== bundle.payload.tax_year) throw new FireTaxPropertyInputError("propertyProfile taxYear must match the validated rule year");
    const currencies = unique(bundle.rules.map(function (rule) { return rule.currency; }));
    if (currencies.length !== 1 || profile.currency !== currencies[0]) throw new FireTaxPropertyInputError("propertyProfile currency must match the active property rules");
    if (!Array.isArray(profile.activeStages) || profile.activeStages.length === 0 || new Set(profile.activeStages).size !== profile.activeStages.length || !profile.activeStages.every(function (stage) { return STAGES.includes(stage); })) {
      throw new FireTaxPropertyInputError("activeStages must contain distinct supported property stages");
    }
  }

  function scopeFor(residence, side) {
    if (!record(residence) || !record(residence.scopes)) throw new FireTaxPropertyInputError("residence must contain jurisdiction scopes");
    if (residence.scopes[side] === "worldwide_income") return "resident";
    if (residence.scopes[side] === "source_income") return "nonresident";
    throw new FireTaxPropertyInputError("residence must resolve the " + side + " taxpayer scope");
  }

  function residenceAlternatives(residence) {
    if (record(residence) && residence.status === "conditional") {
      if (!Array.isArray(residence.branches) || residence.branches.length === 0) {
        throw new FireTaxPropertyInputError("conditional residence requires calculated branches");
      }
      return residence.branches.map(function (branch) {
        return { residence: branch, assumedFacts: {}, unresolvedFacts: Array.isArray(residence.unresolvedFacts) ? residence.unresolvedFacts.slice() : [] };
      });
    }
    return [{ residence: residence, assumedFacts: {}, unresolvedFacts: [] }];
  }

  function compare(value, condition) {
    if (condition.operator === "equals") return value === condition.value;
    if (condition.operator === "not_equals") return value !== condition.value;
    if (condition.operator === "less_than") return value < condition.value;
    if (condition.operator === "less_than_or_equal") return value <= condition.value;
    if (condition.operator === "greater_than") return value > condition.value;
    if (condition.operator === "greater_than_or_equal") return value >= condition.value;
    return condition.value.includes(value);
  }

  function profileValue(profile, operandId, bundle) {
    const operand = bundle.catalog[operandId];
    if (!record(operand) || operand.kind !== "profile") throw new FireTaxPropertyRuleError("operand " + operandId + " is not a profile fact");
    const value = profile[operand.profile_key];
    if (value === undefined || value === null || value === "unknown") {
      throw new FireTaxPropertyInputError(operand.profile_key + " is required by an active property rule");
    }
    if (!valueMatches(value, operand)) throw new FireTaxPropertyInputError(operand.profile_key + " does not match its validated input contract");
    return value;
  }

  function resolveOperand(operandId, profile, bundle, cache, stack) {
    if (Object.prototype.hasOwnProperty.call(cache, operandId)) return cache[operandId];
    const operand = bundle.catalog[operandId];
    if (!record(operand)) throw new FireTaxPropertyRuleError("formula references unknown operand " + operandId);
    if (stack.has(operandId)) throw new FireTaxPropertyRuleError("derived operand cycle reaches " + operandId);
    let value;
    if (operand.kind === "profile") {
      value = profileValue(profile, operandId, bundle);
    } else if (operand.kind === "constant") {
      value = operand.value;
    } else {
      stack.add(operandId);
      const values = operand.derivation.operands.map(function (nestedId) { return resolveOperand(nestedId, profile, bundle, cache, stack); });
      stack.delete(operandId);
      if (operand.derivation.operation === "add") value = values.reduce(function (sum, item) { return sum + item; }, 0);
      if (operand.derivation.operation === "subtract") value = values[0] - values[1];
      if (operand.derivation.operation === "multiply") value = values[0] * values[1];
      if (operand.derivation.operation === "minimum") value = Math.min.apply(Math, values);
      if (operand.derivation.operation === "maximum") value = Math.max.apply(Math, values);
    }
    if (!finite(value)) throw new FireTaxPropertyInputError("operand " + operandId + " did not resolve to a finite amount");
    cache[operandId] = round(value);
    return cache[operandId];
  }

  function progressiveTax(base, bands) {
    let tax = 0;
    bands.forEach(function (band) {
      const upper = band.up_to === null ? base : Math.min(base, band.up_to);
      tax += Math.max(0, upper - band.from) * band.rate;
    });
    return round(tax);
  }

  function auditOperand(operandId, profile, bundle, cache) {
    const operand = bundle.catalog[operandId];
    const audit = {
      operandId: operandId,
      kind: operand.kind,
      value: resolveOperand(operandId, profile, bundle, cache, new Set()),
      currency: operand.currency || null,
      auditRole: operand.audit_role || null
    };
    if (operand.kind === "profile") audit.profileKey = operand.profile_key;
    if (operand.kind === "derived") {
      audit.operation = operand.derivation.operation;
      audit.operands = operand.derivation.operands.map(function (nestedId) {
        return auditOperand(nestedId, profile, bundle, cache);
      });
    }
    return audit;
  }

  function collectAllowances(audits) {
    const found = new Map();
    function visit(audit) {
      if (audit.kind === "constant" && audit.auditRole === "allowance") {
        found.set(audit.operandId, {
          operandId: audit.operandId,
          amount: audit.value,
          currency: audit.currency
        });
      }
      (audit.operands || []).forEach(visit);
    }
    audits.forEach(visit);
    return Array.from(found.values());
  }

  function executeRule(rule, profile, taxpayerScope, bundle) {
    const cache = {};
    const operandValues = rule.formula.operands.map(function (operandId) {
      return resolveOperand(operandId, profile, bundle, cache, new Set());
    });
    let amount;
    if (rule.formula.operation === "add") amount = operandValues.reduce(function (sum, value) { return sum + value; }, 0);
    if (rule.formula.operation === "multiply") amount = operandValues[0] * operandValues[1];
    if (rule.formula.operation === "progressive_rate") amount = progressiveTax(operandValues[0], rule.bands);
    if (rule.floor_at_zero === true) amount = Math.max(0, amount);
    amount = round(amount);
    if (!finite(amount) || amount < 0) throw new FireTaxPropertyInputError("property rule " + rule.id + " calculated an unsupported negative amount");
    const operator = rule.formula.operation === "progressive_rate" ? "progressive_rate" : rule.formula.operation;
    const formulaInputs = rule.formula.operands.map(function (operandId, index) {
      return operandId + "=" + operandValues[index];
    });
    const operandAudit = rule.formula.operands.map(function (operandId) {
      return auditOperand(operandId, profile, bundle, cache);
    });
    return {
      label: rule.explanation,
      stage: rule.lifecycle_stage,
      category: rule.category,
      chargeKind: rule.charge_kind,
      classification: rule.payment_treatment === "prepayment" ? "prepayment" : rule.tax_or_non_tax,
      amount: amount,
      currency: rule.currency,
      formula: operator + "(" + formulaInputs.join(", ") + ") = " + amount,
      assumptions: [rule.explanation, "User-supplied property facts are applied only to this active lifecycle rule."],
      taxYear: rule.tax_year,
      taxpayerScope: taxpayerScope,
      confidence: rule.confidence,
      ruleIds: [rule.id],
      sourceIds: rule.source_ids.slice(),
      effectiveFrom: rule.effective_from,
      retirementCostBoundary: rule.retirement_cost_boundary || null,
      operandAudit: operandAudit,
      allowances: collectAllowances(operandAudit)
    };
  }

  function activeRules(profile, taxpayerScope, bundle) {
    return profile.activeStages.flatMap(function (stage) {
      const scoped = bundle.coverageRules[stage] && bundle.coverageRules[stage][taxpayerScope];
      if (!Array.isArray(scoped) || scoped.length === 0) {
        throw new FireTaxPropertyRuleError("property coverage " + stage + "." + taxpayerScope + " is unavailable");
      }
      return scoped;
    });
  }

  function ruleCouldApplyWithout(rule, skippedOperandId, profile, bundle) {
    return (rule.applies_when || []).every(function (condition) {
      if (condition.operand === skippedOperandId) return true;
      const operand = bundle.catalog[condition.operand];
      const value = profile[operand.profile_key];
      if (value === undefined || value === null || value === "unknown") return true;
      if (!valueMatches(value, operand)) {
        throw new FireTaxPropertyInputError(operand.profile_key + " does not match its validated input contract");
      }
      return compare(value, condition);
    });
  }

  function expandUnknownFacts(alternative, taxpayerScope, bundle) {
    let alternatives = [alternative];
    const candidateRules = activeRules(alternative.profile, taxpayerScope, bundle);
    const conditionOperands = unique(candidateRules.flatMap(function (rule) {
      return (rule.applies_when || []).map(function (condition) { return condition.operand; });
    }));
    conditionOperands.forEach(function (operandId) {
      const operand = bundle.catalog[operandId];
      const key = operand.profile_key;
      const value = alternative.profile[key];
      if (value !== undefined && value !== null && value !== "unknown") return;
      const relevantRules = candidateRules.filter(function (rule) {
        return (rule.applies_when || []).some(function (condition) { return condition.operand === operandId; }) &&
          ruleCouldApplyWithout(rule, operandId, alternative.profile, bundle);
      });
      if (relevantRules.length === 0) return;
      if (key !== "heirRelationship") {
        throw new FireTaxPropertyInputError(key + " is required by an active property branch");
      }
      const supported = operand.allowed_values.slice();
      alternatives = alternatives.flatMap(function (item) {
        return supported.map(function (assumed) {
          return {
            profile: Object.assign({}, item.profile, { [key]: assumed }),
            residence: item.residence,
            assumedFacts: Object.assign({}, item.assumedFacts, { [key]: assumed }),
            unresolvedFacts: unique(item.unresolvedFacts.concat([key])),
            controllingRuleIds: unique((item.controllingRuleIds || []).concat(relevantRules.map(function (rule) { return rule.id; })))
          };
        });
      });
    });

    const rangeOperandIds = unique(candidateRules.filter(function (rule) {
      return record(rule.unknown_operand_range);
    }).map(function (rule) { return rule.unknown_operand_range.operand; }));
    rangeOperandIds.forEach(function (rangeOperandId) {
      alternatives = alternatives.flatMap(function (item) {
        const operand = bundle.catalog[rangeOperandId];
        const key = operand.profile_key;
        const supplied = item.profile[key];
        if (supplied !== undefined && supplied !== null && supplied !== "unknown") return [item];
        const relevantRules = activeRules(item.profile, taxpayerScope, bundle).filter(function (rule) {
          return record(rule.unknown_operand_range) && rule.unknown_operand_range.operand === rangeOperandId &&
            ruleCouldApplyWithout(rule, rangeOperandId, item.profile, bundle);
        });
        if (relevantRules.length === 0) return [item];
        const signatures = unique(relevantRules.map(function (rule) {
          const range = rule.unknown_operand_range;
          return [range.reference_operand, range.minimum_ratio, range.maximum_ratio].join("|");
        }));
        if (signatures.length !== 1) throw new FireTaxPropertyRuleError("active rules disagree on the supported range for " + key);
        const entry = {
          range: relevantRules[0].unknown_operand_range,
          ruleIds: relevantRules.map(function (rule) { return rule.id; })
        };
        const reference = resolveOperand(entry.range.reference_operand, item.profile, bundle, {}, new Set());
        return [entry.range.minimum_ratio, entry.range.maximum_ratio].map(function (ratio) {
          return {
            profile: Object.assign({}, item.profile, { [key]: round(reference * ratio) }),
            residence: item.residence,
            assumedFacts: Object.assign({}, item.assumedFacts, { [key]: round(reference * ratio) }),
            unresolvedFacts: unique(item.unresolvedFacts.concat([key])),
            controllingRuleIds: unique((item.controllingRuleIds || []).concat(entry.ruleIds))
          };
        });
      });
    });
    return alternatives;
  }

  function applies(rule, profile, bundle) {
    return (rule.applies_when || []).every(function (condition) {
      return compare(profileValue(profile, condition.operand, bundle), condition);
    });
  }

  function emptyStage() {
    return { taxTotal: 0, nonTaxTotal: 0, prepaymentTotal: 0, lines: [] };
  }

  function calculateLeaf(alternative, bundle) {
    const taxpayerScope = scopeFor(alternative.residence, bundle.side);
    const stages = {};
    alternative.profile.activeStages.forEach(function (stage) { stages[stage] = emptyStage(); });
    const applicable = activeRules(alternative.profile, taxpayerScope, bundle).filter(function (rule) {
      return applies(rule, alternative.profile, bundle);
    });
    alternative.profile.activeStages.forEach(function (stage) {
      const coveredLines = applicable.filter(function (rule) { return rule.lifecycle_stage === stage; });
      if (coveredLines.length === 0) {
        throw new FireTaxPropertyRuleError("property coverage " + stage + "." + taxpayerScope + " has no executable branch for the supplied facts");
      }
    });
    applicable.forEach(function (rule) {
      const line = executeRule(rule, alternative.profile, taxpayerScope, bundle);
      const stage = stages[rule.lifecycle_stage];
      stage.lines.push(line);
      if (line.classification === "tax") stage.taxTotal = round(stage.taxTotal + line.amount);
      if (line.classification === "non_tax") stage.nonTaxTotal = round(stage.nonTaxTotal + line.amount);
      if (line.classification === "prepayment") stage.prepaymentTotal = round(stage.prepaymentTotal + line.amount);
    });
    const stageTax = function (name) { return stages[name] ? stages[name].taxTotal : 0; };
    const stageNonTax = function (name) { return stages[name] ? stages[name].nonTaxTotal : 0; };
    const stagePrepayment = function (name) { return stages[name] ? stages[name].prepaymentTotal : 0; };
    const annualTax = round(stageTax("annual") + stageTax("rental"));
    const oneTimeTax = round(stageTax("purchase") + stageTax("sale") + stageTax("inheritance") + stageTax("gift"));
    const ownerBoundary = round(Object.values(stages).flatMap(function (stage) { return stage.lines; }).filter(function (line) {
      return line.retirementCostBoundary === "owner_property_tax";
    }).reduce(function (sum, line) { return sum + line.amount; }, 0));
    const allLines = Object.values(stages).flatMap(function (stage) { return stage.lines; });
    return {
      status: "calculated",
      currency: alternative.profile.currency,
      taxYear: alternative.profile.taxYear,
      taxpayerScope: taxpayerScope,
      stages: stages,
      totals: {
        annualTax: annualTax,
        oneTimeTax: oneTimeTax,
        allTax: round(annualTax + oneTimeTax),
        prepayments: round(STAGES.reduce(function (sum, stage) { return sum + stagePrepayment(stage); }, 0)),
        nonTax: round(STAGES.reduce(function (sum, stage) { return sum + stageNonTax(stage); }, 0))
      },
      retirementIntegration: {
        annualTaxBeforeBoundary: annualTax,
        ownerPropertyTaxAlreadyInLivingCosts: ownerBoundary,
        additionalAnnualTaxExpense: round(Math.max(0, annualTax - ownerBoundary)),
        excludedRuleIds: allLines.filter(function (line) { return line.retirementCostBoundary === "owner_property_tax"; }).map(function (line) { return line.ruleIds[0]; }),
        explanation: "Owner property tax already present in retirement living costs is excluded from added annual tax to prevent double counting."
      },
      ruleIds: allLines.map(function (line) { return line.ruleIds[0]; }),
      sourceIds: unique(allLines.flatMap(function (line) { return line.sourceIds; })),
      confidence: lowestConfidence(allLines.map(function (line) { return line.confidence; })),
      assumptions: ["Only selected property lifecycle stages and applicable validated rules are calculated."],
      assumedFacts: Object.assign({}, alternative.assumedFacts)
    };
  }

  function range(values) {
    return { minimum: round(Math.min.apply(Math, values)), maximum: round(Math.max.apply(Math, values)) };
  }

  function aggregateStage(branches, stage) {
    return {
      taxTotal: range(branches.map(function (branch) { return branch.stages[stage] ? branch.stages[stage].taxTotal : 0; })),
      nonTaxTotal: range(branches.map(function (branch) { return branch.stages[stage] ? branch.stages[stage].nonTaxTotal : 0; })),
      prepaymentTotal: range(branches.map(function (branch) { return branch.stages[stage] ? branch.stages[stage].prepaymentTotal : 0; })),
      branchBreakdown: branches.map(function (branch, index) {
        const branchStage = branch.stages[stage] || emptyStage();
        return {
          branchIndex: index,
          taxpayerScope: branch.taxpayerScope,
          assumedFacts: Object.assign({}, branch.assumedFacts),
          taxTotal: branchStage.taxTotal,
          nonTaxTotal: branchStage.nonTaxTotal,
          prepaymentTotal: branchStage.prepaymentTotal,
          lines: branchStage.lines
        };
      })
    };
  }

  function aggregate(branches, alternatives) {
    const activeStages = unique(branches.flatMap(function (branch) { return Object.keys(branch.stages); }));
    const stages = {};
    activeStages.forEach(function (stage) { stages[stage] = aggregateStage(branches, stage); });
    const totalField = function (field) { return range(branches.map(function (branch) { return branch.totals[field]; })); };
    const unresolvedFacts = unique(alternatives.flatMap(function (item) { return item.unresolvedFacts || []; }));
    return {
      status: "conditional",
      currency: branches[0].currency,
      taxYear: branches[0].taxYear,
      taxpayerScope: "conditional",
      stages: stages,
      totals: {
        annualTax: totalField("annualTax"),
        oneTimeTax: totalField("oneTimeTax"),
        allTax: totalField("allTax"),
        prepayments: totalField("prepayments"),
        nonTax: totalField("nonTax")
      },
      retirementIntegration: {
        annualTaxBeforeBoundary: range(branches.map(function (branch) { return branch.retirementIntegration.annualTaxBeforeBoundary; })),
        ownerPropertyTaxAlreadyInLivingCosts: range(branches.map(function (branch) { return branch.retirementIntegration.ownerPropertyTaxAlreadyInLivingCosts; })),
        additionalAnnualTaxExpense: range(branches.map(function (branch) { return branch.retirementIntegration.additionalAnnualTaxExpense; })),
        excludedRuleIds: unique(branches.flatMap(function (branch) { return branch.retirementIntegration.excludedRuleIds; })),
        explanation: "Each supported branch excludes owner property tax already present in retirement living costs to prevent double counting."
      },
      branches: branches,
      unresolvedFacts: unresolvedFacts,
      controllingRuleIds: unique(alternatives.flatMap(function (item) { return item.controllingRuleIds || []; })),
      ruleIds: unique(branches.flatMap(function (branch) { return branch.ruleIds; })),
      sourceIds: unique(branches.flatMap(function (branch) { return branch.sourceIds; })),
      confidence: lowestConfidence(branches.map(function (branch) { return branch.confidence; })),
      assumptions: ["Displayed ranges preserve every supported residence or missing-fact branch; no unknown fact is treated as zero."]
    };
  }

  function calculatePropertyTaxes(propertyProfile, residence, rules) {
    const bundle = selectBundle(rules);
    validateProfileHeader(propertyProfile, bundle);
    let alternatives = residenceAlternatives(residence).map(function (item) {
      return Object.assign(item, { profile: Object.assign({}, propertyProfile), controllingRuleIds: [] });
    });
    alternatives = alternatives.flatMap(function (alternative) {
      const taxpayerScope = scopeFor(alternative.residence, bundle.side);
      return expandUnknownFacts(alternative, taxpayerScope, bundle);
    });
    const branches = alternatives.map(function (alternative) { return calculateLeaf(alternative, bundle); });
    if (branches.length === 1 && alternatives[0].unresolvedFacts.length === 0) return branches[0];
    return aggregate(branches, alternatives);
  }

  return {
    calculatePropertyTaxes: calculatePropertyTaxes,
    FireTaxPropertyInputError: FireTaxPropertyInputError,
    FireTaxPropertyRuleError: FireTaxPropertyRuleError
  };
});
