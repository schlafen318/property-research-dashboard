(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxHongKongUAE = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  const INCOME = [
    ["private_pension", "privatePension"], ["government_pension", "governmentPension"],
    ["social_security", "socialSecurity"], ["dividends", "dividends"], ["interest", "interest"],
    ["realized_gains", "realizedGains"], ["retirement_account_withdrawal", "retirementAccountWithdrawal"],
    ["rental_income", "rentalIncome"], ["employment_consulting", "employmentConsulting"],
  ];
  const STAGES = ["purchase", "annual", "rental", "sale", "inheritance", "gift"];

  function record(value) { return value !== null && typeof value === "object" && !Array.isArray(value); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }

  function selectedSources(sourceIds, sources) {
    const byId = Object.fromEntries((sources || []).map(function (source) { return [source.id, source]; }));
    return sourceIds.map(function (id) { return clone(byId[id]); });
  }

  function audit(id, type, category, currency, sourceIds, extra) {
    return Object.assign({
      id: id, type: type, tax_year: 2026, taxpayer_scope: ["resident", "nonresident"],
      category: category, currency: currency, source_ids: sourceIds.slice(), effective_from: "2026-01-01",
      checked_on: "2026-09-01", review_interval_days: 90, confidence: "high",
      recheck_trigger: "Recheck the linked official source before the next tax-year release.",
      explanation: "Apply the validated Hong Kong-to-Dubai profile rule.",
    }, extra || {});
  }

  function residenceRules(definition, currency, sources) {
    const destinationSource = ["uae-tax-residence-2026"];
    const homeSource = ["hk-uae-treaty-2026", "hk-territorial-individual-tax-2026"];
    const destination = {
      schema_version: 1, tax_year: 2026, checked_on: "2026-09-01",
      operand_catalog: {
        days_in_destination: { kind: "profile", profile_key: "daysInDestination", value_type: "number", minimum: 0, maximum: 365, integer: true, day_count: true },
        threshold: { kind: "constant", value_type: "number", value: 183 },
      },
      sources: selectedSources(destinationSource, sources), active_jurisdiction_id: "dubai",
      jurisdictions: { dubai: {
        id: "dubai", label: "Dubai", synthetic: false, detailed_enabled: true,
        resident_scope: "worldwide_income", nonresident_scope: "source_income",
        residence_logic: { operation: "any", rule_ids: ["uae-183-day-residence-2026"] },
        rules: [audit("uae-183-day-residence-2026", "residence_test", "tax_residence", currency, destinationSource, {
          taxpayer_scope: ["individual"], formula: { operation: "greater_than_or_equal", operands: ["days_in_destination", "threshold"] },
          resident_when: true, explanation: "The supported profile uses the UAE 183-day tax-residence route.",
        })],
      } },
    };
    const home = {
      schema_version: 1, tax_year: 2026, checked_on: "2026-09-01",
      operand_catalog: { home_resident: { kind: "profile", profile_key: "homeTreatyResident", value_type: "boolean" } },
      sources: selectedSources(homeSource, sources), active_jurisdiction_id: "hong-kong",
      jurisdictions: { "hong-kong": {
        id: "hong-kong", label: "Hong Kong", synthetic: false, detailed_enabled: true,
        resident_scope: "worldwide_income", nonresident_scope: "source_income",
        residence_logic: { operation: "any", rule_ids: ["hong-kong-treaty-residence-2026"] },
        rules: [audit("hong-kong-treaty-residence-2026", "residence_test", "tax_residence", currency, homeSource, {
          taxpayer_scope: ["individual"], formula: { operation: "flag", operands: ["home_resident"] }, resident_when: true,
          explanation: "The factual Article 4 sequence—Hong Kong domestic residence, permanent homes, closest personal/economic relations, habitual abode, and right-of-abode/nationality where needed—must produce a supported UAE treaty outcome before this flag is false.",
        })],
      } },
    };
    return { destination: destination, home: home };
  }

  function incomeRules(id, side, currency, sourceIds, sources) {
    const catalog = {};
    const rules = INCOME.map(function (entry) {
      const category = entry[0], profileKey = entry[1], operandId = "income_" + category;
      catalog[operandId] = { kind: "profile", profile_key: profileKey, value_type: "money", currency: currency };
      const rule = audit(id + "-" + category.replace(/_/g, "-") + "-2026", "rate_band", category, currency, sourceIds, {
        formula: { operation: "progressive_rate", operands: [operandId] }, bands: [{ from: 0, up_to: null, rate: 0 }], no_tax: true,
        explanation: side === "destination"
          ? "The UAE does not levy individual income tax; the supported profile excludes UAE business or consulting activity."
          : "The supported profile excludes Hong Kong-source income, so only non-Hong Kong-source amounts reach this territorial home overlay.",
      });
      if (category === "retirement_account_withdrawal") {
        catalog.retirement_classification = { kind: "profile", profile_key: "retirementAccountClassification", value_type: "string", allowed_values: ["personal_investment"] };
        rule.account_classification_operand = "retirement_classification";
        rule.supported_account_classifications = ["personal_investment"];
      }
      return rule;
    });
    return {
      schema_version: 1, tax_year: 2026, checked_on: "2026-09-01", operand_catalog: catalog,
      sources: selectedSources(sourceIds, sources), active_jurisdiction_id: id,
      jurisdictions: { [id]: { id: id, label: id === "dubai" ? "Dubai" : "Hong Kong", synthetic: false, detailed_enabled: true, calculation_side: side, resident_scope: "worldwide_income", nonresident_scope: "source_income", rules: rules } },
    };
  }

  function propertyRule(id, stage, currency, sources, config) {
    const sourceIds = config.sourceIds;
    return audit(id, "property_charge", "property_" + stage, currency, sourceIds, {
      lifecycle_stage: stage, charge_kind: config.kind, tax_or_non_tax: config.classification,
      payment_treatment: "current_liability", formula: config.formula, rate: config.rate,
      rate_operand: config.rateOperand, amount: config.amount, amount_operand: config.amountOperand,
      no_tax: config.noTax === true, retirement_cost_boundary: config.boundary,
      explanation: config.explanation,
    });
  }

  function propertyRules(definition, profile, currency, sources) {
    const constants = definition.runtime_definition.rule_constants;
    const price = profile.destination.property.purchasePrice;
    const giftValuation = profile.destination.property.giftValuation;
    const aedPerCurrency = Number(profile.destination.property.aedPerCurrency);
    if (!Number.isFinite(aedPerCurrency) || aedPerCurrency <= 0) throw new TypeError("A current AED conversion rate is required");
    const aed = function (amount) { return Math.round((amount / aedPerCurrency) * 100) / 100; };
    const trusteeAed = price * aedPerCurrency >= 500000 ? 4000 : 2000;
    const giftTrusteeAed = giftValuation * aedPerCurrency >= 2000000 ? 4000 : 2000;
    const catalog = {
      purchase_price: { kind: "profile", profile_key: "purchasePrice", value_type: "money", currency: currency },
      sale_price: { kind: "profile", profile_key: "salePrice", value_type: "money", currency: currency },
      annual_rent: { kind: "profile", profile_key: "annualRent", value_type: "money", currency: currency },
      annual_service_charges: { kind: "profile", profile_key: "annualServiceCharges", value_type: "money", currency: currency },
      annual_housing_fee: { kind: "profile", profile_key: "annualHousingFee", value_type: "money", currency: currency },
      gift_valuation: { kind: "profile", profile_key: "giftValuation", value_type: "money", currency: currency },
      one_rate: { kind: "constant", value_type: "number", value: 1 }, zero_rate: { kind: "constant", value_type: "number", value: 0 },
      buyer_rate: { kind: "constant", value_type: "number", value: constants.buyer_sale_registration_rate },
      seller_rate: { kind: "constant", value_type: "number", value: constants.seller_sale_registration_rate },
      gift_rate: { kind: "constant", value_type: "number", value: constants.gift_registration_rate },
      purchase_fixed: { kind: "constant", value_type: "money", currency: currency, value: aed(constants.title_deed_aed + constants.unit_map_aed + constants.knowledge_and_innovation_aed + trusteeAed * (1 + constants.vat_rate)) },
      inheritance_fixed: { kind: "constant", value_type: "money", currency: currency, value: aed(constants.inheritance_registration_aed + constants.title_deed_aed + constants.unit_map_aed + constants.knowledge_and_innovation_aed + constants.inheritance_partner_fee_aed * (1 + constants.vat_rate)) },
      gift_fixed: { kind: "constant", value_type: "money", currency: currency, value: aed(constants.title_deed_aed + constants.unit_map_aed + constants.knowledge_and_innovation_aed + giftTrusteeAed * (1 + constants.vat_rate)) },
    };
    const dld = ["dld-sale-registration-2026"], gift = ["dld-gift-registration-2026"], inheritance = ["dld-inheritance-registration-2026"], fx = ["cbuae-aed-usd-rate-2026"];
    const service = ["dld-service-charge-index-2026"], vat = ["uae-residential-property-vat-2026", "uae-individual-tax-2026"];
    const rules = [
      propertyRule("dubai-purchase-registration-2026", "purchase", currency, sources, { sourceIds: dld, kind: "registration_fee", classification: "non_tax", formula: { operation: "multiply", operands: ["purchase_price", "buyer_rate"] }, rate: constants.buyer_sale_registration_rate, rateOperand: "buyer_rate", explanation: "Buyer share of the DLD sale-registration fee under the standard equal allocation." }),
      propertyRule("dubai-purchase-services-2026", "purchase", currency, sources, { sourceIds: dld.concat(fx), kind: "registration_service_fees", classification: "non_tax", formula: { operation: "add", operands: ["purchase_fixed"] }, amount: catalog.purchase_fixed.value, amountOperand: "purchase_fixed", explanation: "Current DLD title, unit-map, knowledge, innovation and trustee service fees, including VAT only on the trustee service; AED amounts use the cited CBUAE conversion." }),
      propertyRule("dubai-annual-service-charge-2026", "annual", currency, sources, { sourceIds: service, kind: "service_charge", classification: "non_tax", formula: { operation: "multiply", operands: ["annual_service_charges", "one_rate"] }, rate: 1, rateOperand: "one_rate", explanation: "User-supplied property-specific service charge from the DLD index; no universal rate is assumed." }),
      propertyRule("dubai-annual-housing-fee-2026", "annual", currency, sources, { sourceIds: ["dubai-municipality-housing-fee-2026"], kind: "municipality_housing_fee", classification: "non_tax", formula: { operation: "multiply", operands: ["annual_housing_fee", "one_rate"] }, rate: 1, rateOperand: "one_rate", explanation: "User-supplied Dubai Municipality housing fee from the owned-unit property bill; it is shown as a fee rather than relabelled as income or property tax." }),
      propertyRule("dubai-residential-rental-no-tax-2026", "rental", currency, sources, { sourceIds: vat, kind: "residential_rental_tax", classification: "tax", formula: { operation: "multiply", operands: ["annual_rent", "zero_rate"] }, rate: 0, rateOperand: "zero_rate", noTax: true, explanation: "Personally held residential rent is outside UAE individual income tax and residential rent carries no owner-charged VAT in this profile." }),
      propertyRule("dubai-sale-registration-2026", "sale", currency, sources, { sourceIds: dld, kind: "sale_registration_fee", classification: "non_tax", formula: { operation: "multiply", operands: ["sale_price", "seller_rate"] }, rate: constants.seller_sale_registration_rate, rateOperand: "seller_rate", explanation: "Seller share of the DLD sale-registration fee under the standard equal allocation." }),
      propertyRule("dubai-inheritance-registration-2026", "inheritance", currency, sources, { sourceIds: inheritance.concat(fx), kind: "inheritance_registration_fee", classification: "non_tax", formula: { operation: "add", operands: ["inheritance_fixed"] }, amount: catalog.inheritance_fixed.value, amountOperand: "inheritance_fixed", explanation: "Current DLD inheritance title-transfer, title, unit-map, knowledge, innovation and partner service fees; AED amounts use the cited CBUAE conversion." }),
      propertyRule("dubai-gift-registration-2026", "gift", currency, sources, { sourceIds: gift.concat(fx), kind: "gift_registration_fee", classification: "non_tax", formula: { operation: "multiply", operands: ["gift_valuation", "gift_rate"] }, rate: constants.gift_registration_rate, rateOperand: "gift_rate", explanation: "Qualifying first-degree-family DLD gift registration percentage applied to the user-supplied DLD property valuation; the minimum branch check uses the cited CBUAE conversion." }),
      propertyRule("dubai-gift-services-2026", "gift", currency, sources, { sourceIds: gift.concat(fx), kind: "gift_service_fees", classification: "non_tax", formula: { operation: "add", operands: ["gift_fixed"] }, amount: catalog.gift_fixed.value, amountOperand: "gift_fixed", explanation: "Current DLD gift title, unit-map, knowledge, innovation and trustee service fees; AED amounts use the cited CBUAE conversion." }),
    ];
    const coverage = {};
    STAGES.forEach(function (stage) {
      const ids = rules.filter(function (rule) { return rule.lifecycle_stage === stage; }).map(function (rule) { return rule.id; });
      const treatment = stage === "rental" ? "no_tax" : "supported";
      coverage[stage] = { resident: { treatment: treatment, rule_ids: ids }, nonresident: { treatment: treatment, rule_ids: ids } };
    });
    const sourceIds = Array.from(new Set(rules.flatMap(function (rule) { return rule.source_ids; })));
    return {
      schema_version: 1, tax_year: 2026, checked_on: "2026-09-01", operand_catalog: catalog,
      sources: selectedSources(sourceIds, sources), active_jurisdiction_id: "dubai",
      jurisdictions: { dubai: { id: "dubai", label: "Dubai", synthetic: false, detailed_enabled: true, calculation_side: "destination", resident_scope: "worldwide_income", nonresident_scope: "source_income", property_coverage: coverage, rules: rules } },
    };
  }

  function buildRuntimeBundle(definition, profile, sources) {
    if (!record(definition) || !record(profile) || definition.runtime_definition.factory !== "hong-kong-to-dubai-v1") throw new TypeError("Unsupported detailed profile factory");
    if (!record(profile.destination) || !record(profile.destination.property) || profile.destination.property.enabled !== false) throw new TypeError("The enabled Hong Kong to Dubai exact factory is renter-only; owned-property rules are not published.");
    const currency = profile.destination.income.currency;
    const residence = residenceRules(definition, currency, sources);
    const destinationIncomeSources = ["uae-individual-tax-2026", "uae-natural-person-business-2026"];
    const homeIncomeSources = ["hk-territorial-individual-tax-2026", "hk-uae-treaty-2026"];
    const destinationIncome = incomeRules("dubai", "destination", currency, destinationIncomeSources, sources);
    const homeIncome = incomeRules("hong-kong", "home", currency, homeIncomeSources, sources);
    const noProperty = function (id, side) { return { schema_version: 1, tax_year: 2026, checked_on: "2026-09-01", operand_catalog: {}, sources: [], active_jurisdiction_id: id, jurisdictions: { [id]: { id: id, label: id === "dubai" ? "Dubai" : "Hong Kong", synthetic: false, detailed_enabled: true, calculation_side: side, resident_scope: "worldwide_income", nonresident_scope: "source_income", property_coverage: {}, rules: [] } } }; };
    const destinationProperty = noProperty("dubai", "destination");
    const homeProperty = noProperty("hong-kong", "home");
    return {
      residence: residence,
      rules: {
        residence: residence,
        destination: { income: destinationIncome, credits: [], property: destinationProperty },
        continuingHome: { income: homeIncome, credits: [], property: homeProperty },
      },
    };
  }

  return { buildRuntimeBundle: buildRuntimeBundle };
});
