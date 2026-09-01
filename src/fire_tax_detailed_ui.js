(function (root, factory) {
  const detailed = typeof module === "object" && module.exports ? require("./fire_tax_detailed.js") : root && root.GHAFireTaxDetailed;
  const explain = typeof module === "object" && module.exports ? require("./fire_tax_explain.js") : root && root.GHAFireTaxExplain;
  const profile = typeof module === "object" && module.exports ? require("./fire_tax_profile.js") : root && root.GHAFireTaxProfile;
  const hkUae = typeof module === "object" && module.exports ? require("./fire_tax_hk_uae.js") : root && root.GHAFireTaxHongKongUAE;
  const api = factory(detailed, explain, profile, hkUae);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxDetailedUI = api;
})(typeof window !== "undefined" ? window : null, function (detailed, explain, profileApi, hkUaeApi) {
  "use strict";

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function escapeHtml(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function supportedProfile(destinationId, payload, homeId) {
    const profiles = record(payload) && record(payload.supported_profiles) ? payload.supported_profiles : {};
    return Object.keys(profiles).map(function (id) { return profiles[id]; }).find(function (item) {
      return record(item) && item.id && item.destination_id === destinationId && item.home_jurisdiction_id === homeId;
    }) || null;
  }

  function hongKongDomesticResidence(facts) {
    facts = record(facts) ? facts : {};
    const currentDays = Number(facts.daysInHome);
    const validDays = function (value) { return Number.isInteger(value) && value >= 0 && value <= 366; };
    if (!validDays(currentDays)) return "incomplete";
    if (currentDays > 180) return "resident";
    const previousDays = Number(facts.daysInHomePreviousYear);
    if (!validDays(previousDays)) return "incomplete";
    if (currentDays + previousDays > 300) return "resident";
    if (!["yes", "no", "not_sure"].includes(facts.followingYearDaysKnown)) return "incomplete";
    if (facts.followingYearDaysKnown !== "yes") return "unresolved";
    const followingDays = Number(facts.daysInHomeFollowingYear);
    if (!validDays(followingDays)) return "incomplete";
    if (currentDays + followingDays > 300) return "resident";
    const settledFacts = [facts.hongKongSettledDailyLife, facts.hongKongFixedHome, facts.hongKongWorkOrBusiness, facts.hongKongCloseFamily];
    if (settledFacts.some(function (value) { return !["yes", "no", "not_sure"].includes(value); })) return "incomplete";
    if (settledFacts.includes("not_sure")) return "unresolved";
    if (facts.hongKongSettledDailyLife === "yes") return "resident";
    return settledFacts.every(function (value) { return value === "no"; }) ? "not_resident" : "unresolved";
  }

  function profileAccess(destinationId, payload, profile, facts) {
    const homeId = record(profile) && typeof profile.homeJurisdictionId === "string" ? profile.homeJurisdictionId : "";
    if (!homeId) return { available: false, reason: "Choose your home tax jurisdiction before using exact refinement." };
    const definition = supportedProfile(destinationId, payload, homeId);
    if (!record(definition) || definition.detailed_enabled !== true) return { available: false, reason: "Complete current rules do not yet cover this destination together with your home tax jurisdiction." };
    if (definition.synthetic === true) return { available: false, reason: "Synthetic rules cannot be used for a personal estimate." };
    const requiredIncome = ["private_pension", "government_pension", "social_security", "dividends", "interest", "realized_gains", "retirement_account_withdrawal", "rental_income", "employment_consulting"];
    const capabilities = { supported_activity_types: ["retired_nonworking"], supported_retirement_accounts: ["personal_investment"], supported_housing_plans: ["rent"] };
    const runtime = definition.runtime_definition;
    if (definition.tax_year !== payload.tax_year || !record(runtime) || runtime.factory !== "hong-kong-to-dubai-v1" ||
      Object.keys(capabilities).some(function (key) { return !Array.isArray(runtime[key]) || runtime[key].length !== capabilities[key].length || runtime[key].some(function (value) { return !capabilities[key].includes(value); }); }) ||
      !record(definition.runtime_rule_graph) || definition.runtime_rule_graph.schema_version !== 1 ||
      !requiredIncome.every(function (category) { return (definition.income_categories || []).includes(category); }) ||
      !Array.isArray(definition.property_lifecycle) || definition.property_lifecycle.length !== 0) {
      return { available: false, reason: "The validated rule coverage for this exact profile is incomplete." };
    }
    const sources = Object.fromEntries((payload.sources || []).filter(record).map(function (source) { return [source.id, source]; }));
    if (!Array.isArray(definition.source_ids) || definition.source_ids.length === 0 || definition.source_ids.some(function (id) {
      return !record(sources[id]) || sources[id].source_kind !== "official" || !/^https:\/\//.test(sources[id].url || "") || !/^\d{4}-\d{2}-\d{2}$/.test(sources[id].checked_on || "") || !/^\d{4}-\d{2}-\d{2}$/.test(sources[id].effective_from || "");
    })) return { available: false, reason: "The complete official source set for this profile is unavailable." };
    if (record(facts)) {
      if (Number(facts.annualPension || 0) > 0) return { available: false, reason: "A pension needs its payer country, treaty and withholding rules; this exact profile currently requires zero pension income." };
      if (Number(facts.annualOtherIncome || 0) > 0) return { available: false, reason: "Generic other income cannot be source-classified safely; this exact profile currently requires it to be zero." };
      if (Number(facts.annualRentalIncome || 0) > 0) return { available: false, reason: "Rental income needs the property location and licensed-versus-unlicensed letting rules; this exact profile currently requires it to be zero." };
      if (["annualGovernmentPension", "annualDividends", "annualInterest", "annualRealizedGains"].some(function (key) { return Number(facts[key] || 0) > 0; })) return { available: false, reason: "Separately received pension or investment income needs payer/source-country, treaty and withholding rules; this exact profile requires those amounts to be included in the after-tax portfolio return or set to zero." };
      if (Number(facts.propertyPrice || 0) > 0 || ["buy_now", "buy_retirement"].includes(facts.housingPlan)) return { available: false, reason: "Exact Dubai purchase and ownership tax coverage is not enabled because official sources do not yet establish every potentially applicable property-tax branch." };
      if (facts.housingPlan && !runtime.supported_housing_plans.includes(facts.housingPlan)) return { available: false, reason: "This exact profile currently covers renting in Dubai only." };
      if (facts.daysInDestination < 183) return { available: false, reason: "This exact profile requires at least 183 days in the UAE during the relevant 12-month period." };
      if (facts.explicitReturnProvided === false) return { available: false, reason: "Enter the required after-fees-and-tax portfolio return before exact refinement." };
      if (facts.requireCompleteEligibility === true && (facts.explicitReturnProvided !== true || !Number.isFinite(Number(facts.selectedAfterTaxReturn)) || Number(facts.selectedAfterTaxReturn) <= -1 || Number(facts.selectedAfterTaxReturn) > 1)) return { available: false, reason: "A finite after-fees-and-tax portfolio return is required for exact refinement." };
      const hongKongResidence = hongKongDomesticResidence(facts);
      if (hongKongResidence === "resident") return { available: false, reason: "This narrow exact profile is unavailable when the supported facts indicate Hong Kong residence or possible dual residence." };
      if (hongKongResidence === "unresolved") return { available: false, reason: "Hong Kong residence remains possible or uncertain from these facts, so exact refinement is unavailable." };
      if (facts.requireCompleteEligibility === true && hongKongResidence === "incomplete") return { available: false, reason: "Complete the factual Hong Kong residence questions before exact refinement." };
      if (facts.hasHongKongSourceIncome === true) return { available: false, reason: "Hong Kong-source income requires a broader Hong Kong calculation than this profile supports." };
      if (facts.hasHongKongProperty === true) return { available: false, reason: "A continuing Hong Kong property requires the Hong Kong property lifecycle overlay." };
      if (facts.activityType && !runtime.supported_activity_types.includes(facts.activityType)) return { available: false, reason: "This exact profile is limited to a retired, nonworking period with no employment, business or consulting activity." };
      if (Number(facts.annualEmploymentIncome || facts.annualEmploymentConsulting || facts.employmentConsulting || 0) > 0) return { available: false, reason: "This exact profile is limited to a retired, nonworking period; UAE salary, employment, business and consulting amounts must be zero." };
      if (facts.retirementAccountClassification && !runtime.supported_retirement_accounts.includes(facts.retirementAccountClassification)) return { available: false, reason: "This profile covers ordinary personal investments, not retirement-scheme withdrawals." };
      if (facts.dependableIncomeIndexingCompatible === false) return { available: false, reason: "This exact retirement projection currently requires all non-zero dependable income to use the same inflation-linking choice." };
      if (facts.exitPlan || facts.propertyType || facts.financingType || facts.giftRelationship) return { available: false, reason: "Owned-property lifecycle facts are outside this renter-only exact profile." };
    }
    return { available: true, definition: definition };
  }

  function jurisdictionAccess(destinationId, payload, profile) {
    if (record(payload) && record(payload.supported_profiles)) return profileAccess(destinationId, payload, profile);
    const entry = record(payload) && record(payload.jurisdictions) ? payload.jurisdictions[destinationId] : null;
    if (!record(entry) || entry.detailed_enabled !== true) return { available: false, reason: "No complete current exact-rule set is enabled for this destination." };
    if (entry.synthetic === true) return { available: false, reason: "Synthetic rules cannot be used for a personal estimate." };
    const homeId = record(profile) && typeof profile.homeJurisdictionId === "string" ? profile.homeJurisdictionId : "";
    if (!homeId) return { available: false, reason: "Choose your home tax jurisdiction before using exact refinement." };
    if (!Array.isArray(entry.supported_home_jurisdiction_ids) || !entry.supported_home_jurisdiction_ids.includes(homeId)) {
      return { available: false, reason: "Complete current rules do not yet cover this destination together with your home tax jurisdiction." };
    }
    const bundle = record(entry.runtime_bundles) ? entry.runtime_bundles[homeId] : null;
    if (!record(bundle) || !record(bundle.rules)) return { available: false, reason: "The validated destination-and-home calculation bundle is unavailable." };
    return { available: true, jurisdiction: entry, bundle: bundle };
  }

  function buildDetailedProfile(definition, planningFacts, answers) {
    if (!record(definition) || !record(planningFacts) || !record(answers)) throw new TypeError("Definition, planning facts and detailed answers are required");
    const year = definition.tax_year || 2026;
    const currency = planningFacts.currency || "USD";
    const source = definition.destination_id || "dubai";
    const income = {
      taxYear: year,
      currency: currency,
      privatePension: Number(planningFacts.annualPension || 0),
      governmentPension: Number(answers.annualGovernmentPension || 0),
      socialSecurity: Number(planningFacts.annualOtherIncome || 0),
      dividends: Number(answers.annualDividends || 0),
      interest: Number(answers.annualInterest || 0),
      realizedGains: Number(answers.annualRealizedGains || 0),
      retirementAccountWithdrawal: Number(planningFacts.annualWithdrawals || 0),
      retirementAccountClassification: answers.retirementAccountClassification || "personal_investment",
      rentalIncome: Number(planningFacts.annualRentalIncome || 0),
      employmentConsulting: 0,
      incomeSourceJurisdictions: {
        private_pension: source, government_pension: source, social_security: source,
        dividends: source, interest: source, realized_gains: source,
        retirement_account_withdrawal: source, rental_income: source, employment_consulting: source,
      },
    };
    const price = Number(planningFacts.propertyPrice || 0);
    const constants = record(definition.runtime_definition) && record(definition.runtime_definition.rule_constants) ? definition.runtime_definition.rule_constants : {};
    const aedPerCurrency = Number(planningFacts.aedPerCurrency || 0);
    const priceAed = price * aedPerCurrency;
    const trusteeAed = priceAed >= 500000 ? 4000 : 2000;
    const fixedPurchaseAed = Number(constants.title_deed_aed || 0) + Number(constants.unit_map_aed || 0) + Number(constants.knowledge_and_innovation_aed || 0) + trusteeAed * (1 + Number(constants.vat_rate || 0));
    const purchaseFees = price > 0 && aedPerCurrency > 0 ? price * Number(constants.buyer_sale_registration_rate || 0) + fixedPurchaseAed / aedPerCurrency : 0;
    const annualPropertyCosts = Number(answers.annualServiceCharges || 0) + Number(answers.annualHousingFee || 0);
    const dependableIncomeIndexed = planningFacts.hasLiveDependableIncome === true ? planningFacts.dependableIncomeIndexed === true : answers.detailedIncomeIndexed === true;
    const activeStages = price > 0 ? ["purchase", "annual"] : [];
    if (["rental", "mixed"].includes(planningFacts.propertyUse)) activeStages.push("rental");
    if (["sale", "gift", "inheritance"].includes(answers.exitPlan)) activeStages.push(answers.exitPlan);
    const property = {
      enabled: price > 0, taxYear: year, currency: currency, activeStages: activeStages,
      purchasePrice: price, officialAssessmentBase: price, ownershipShare: 1,
      financingBalance: Number(answers.financingBalance || 0), propertyUse: planningFacts.propertyUse || "personal",
      annualRent: Number(planningFacts.annualRentalIncome || 0), deductibleExpenses: Number(answers.deductibleRentalExpenses || 0),
      acquisitionBasis: price, improvements: Number(answers.propertyImprovements || 0), salePrice: Number(answers.expectedSalePrice || price),
      holdingPeriodYears: Number(planningFacts.horizonYears || 1), heirRelationship: answers.giftRelationship || "first_degree_family",
      transferType: answers.exitPlan || "keep", annualServiceCharges: Number(answers.annualServiceCharges || 0),
      annualHousingFee: Number(answers.annualHousingFee || 0), propertyType: answers.propertyType || "villa_or_apartment", giftValuation: Number(answers.expectedGiftValuation || 0),
    };
    return {
      residence: {
        taxYear: year, daysInDestination: Number(answers.daysInDestination), destinationAvailableHome: false,
        daysInHome: Number(answers.daysInHome), homeAvailableHome: false, homeTreatyResident: false,
        familyTies: "unknown", economicTies: "unknown", splitYear: false,
      },
      destination: { income: income, property: property },
      continuingHome: { enabled: false },
      retirement: {
        baseInput: {
          currentAge: Number(planningFacts.currentAge), retirementAge: Number(planningFacts.retirementAge), horizonYears: Number(planningFacts.horizonYears),
          expenseCategories: [{ amount: Number(planningFacts.annualSpending || 0), inflationRate: Number(planningFacts.generalInflation || 0) }, { amount: annualPropertyCosts, inflationRate: Number(planningFacts.generalInflation || 0) }],
          incomeStreams: [], housingPlan: planningFacts.housingPlan || "rent", propertyPrice: price,
          propertyInflation: Number(planningFacts.propertyInflation || 0), acquisitionCostRate: price > 0 ? purchaseFees / price : 0, generalInflation: Number(planningFacts.generalInflation || 0), emergencyReserveMonths: Number(planningFacts.emergencyReserveMonths || 0),
          expectedPortfolioReturn: Number(planningFacts.selectedAfterTaxReturn), monthlyIncomeBeforeRetirement: Number(planningFacts.monthlyIncomeBeforeRetirement || 0), incomeInvestedRate: Number(planningFacts.incomeInvestedRate || 0),
        },
        selectedAfterTaxReturn: Number(planningFacts.selectedAfterTaxReturn), returnBasis: "after_fees_and_tax",
        dependableIncomeCategories: ["private_pension", "government_pension", "social_security", "dividends", "interest", "realized_gains", "rental_income", "employment_consulting"],
        returnCoveredCategories: ["retirement_account_withdrawal"],
        annualExpenseCategories: [], dependableIncomeIndexed: dependableIncomeIndexed, dependableIncomeInflationRate: dependableIncomeIndexed ? Number(planningFacts.generalInflation || 0) : 0,
        propertyRentalTaxTreatment: "included_in_income_tax", planningRange: planningFacts.planningRange || null,
      },
    };
  }

  function questionMarkup(question) {
    if (!record(question) || typeof question.id !== "string" || typeof question.fact !== "string" || typeof question.label !== "string") return "";
    const id = "fire-tax-question-" + question.id;
    const helpId = id + "-help";
    const accepted = question.acceptedValues;
    let control = "";
    if (question.control === "number" && record(accepted)) {
      control = '<input id="' + escapeHtml(id) + '" name="' + escapeHtml(question.fact) + '" type="number" aria-describedby="' + escapeHtml(helpId) + '" min="' + escapeHtml(accepted.min) + '" max="' + escapeHtml(accepted.max) + '" step="' + escapeHtml(accepted.step) + '" required>';
    } else if (question.control === "date" && record(accepted)) {
      control = '<input id="' + escapeHtml(id) + '" name="' + escapeHtml(question.fact) + '" type="date" aria-describedby="' + escapeHtml(helpId) + '" min="' + escapeHtml(accepted.min) + '" max="' + escapeHtml(accepted.max) + '" required>';
    } else if (question.control === "checkbox") {
      control = '<input id="' + escapeHtml(id) + '" name="' + escapeHtml(question.fact) + '" type="checkbox" aria-describedby="' + escapeHtml(helpId) + '">';
    } else if ((question.control === "select" || question.control === "radio") && Array.isArray(accepted)) {
      const optionLabel = function (value) {
        const option = Array.isArray(question.options) ? question.options.find(function (candidate) { return candidate && candidate.value === value; }) : null;
        return option && typeof option.label === "string" ? option.label : value;
      };
      if (question.control === "select") {
        control = '<select id="' + escapeHtml(id) + '" name="' + escapeHtml(question.fact) + '" aria-describedby="' + escapeHtml(helpId) + '" required><option value="">Choose one</option>' + accepted.map(function (value) { return '<option value="' + escapeHtml(value) + '">' + escapeHtml(optionLabel(value)) + "</option>"; }).join("") + "</select>";
      } else {
        control = accepted.map(function (value, index) {
          const optionId = id + "-" + index;
          return '<label for="' + escapeHtml(optionId) + '"><input id="' + escapeHtml(optionId) + '" type="radio" name="' + escapeHtml(question.fact) + '" value="' + escapeHtml(value) + '" aria-describedby="' + escapeHtml(helpId) + '"' + (index === 0 ? " required" : "") + '> ' + escapeHtml(optionLabel(value)) + "</label>";
        }).join("");
        return '<fieldset class="field"><legend>' + escapeHtml(question.label) + '</legend>' + control + '<p class="hint" id="' + escapeHtml(helpId) + '">' + escapeHtml(question.reason || "This fact can change the calculation.") + "</p></fieldset>";
      }
    }
    if (!control) return "";
    return '<div class="field"><label for="' + escapeHtml(id) + '">' + escapeHtml(question.label) + '</label>' + control + '<p class="hint" id="' + escapeHtml(helpId) + '">' + escapeHtml(question.reason || "This fact can change the calculation.") + "</p></div>";
  }

  function amountRange(value) {
    if (typeof value === "number" && Number.isFinite(value)) return { minimum: value, maximum: value };
    if (record(value) && Number.isFinite(value.minimum) && Number.isFinite(value.maximum)) return value;
    return null;
  }

  function amountText(value, currency) {
    const range = amountRange(value);
    if (!range) return "—";
    const format = function (amount) { return currency + " " + Math.round(amount).toLocaleString("en-US"); };
    return range.minimum === range.maximum ? format(range.minimum) : format(range.minimum) + "–" + format(range.maximum);
  }

  function sourceLinks(sourceIds, sourceById) {
    return (sourceIds || []).map(function (id) {
      const source = sourceById[id];
      if (!record(source) || typeof source.url !== "string" || !/^https:\/\//.test(source.url)) return escapeHtml(id);
      return '<a href="' + escapeHtml(source.url) + '" rel="noopener noreferrer">' + escapeHtml(source.publisher || id) + "</a>";
    }).join(", ");
  }

  function auditValueText(line, currency) {
    if (line.notApplicable === true) return "N/A";
    if (line.valueType === "percentage") {
      const percentage = Number(line.percentage);
      if (!Number.isFinite(percentage)) return "—";
      return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(percentage * 100) + "%";
    }
    if (line.amountRange !== undefined) return amountText(line.amountRange, line.currency || currency);
    if (line.amount !== undefined) return amountText(line.amount, line.currency || currency);
    return "—";
  }

  function resultMarkup(result, auditSections, sources) {
    if (!record(result) || !record(result.totals)) return '<p role="status" aria-live="polite">A refined result is not available.</p>';
    const currency = result.currency || "";
    const projection = record(result.retirementProjection) ? result.retirementProjection : {};
    const branchLabel = function (scenario) {
      const identity = record(scenario.branchIdentity) ? scenario.branchIdentity : {};
      const labels = {
        likely_destination_resident: "UAE domestic 183-day route; not a Hong Kong resident",
        likely_home_resident: "Hong Kong resident",
        dual_resident_treaty_destination: "Treaty resident in the UAE",
        unresolved: "Residence facts unresolved",
      };
      return labels[identity.residenceStatus] || (scenario.id === "resident" ? "Resident branch" : scenario.id === "nonresident" ? "Non-resident branch" : "Calculated profile");
    };
    const scenarios = Array.isArray(result.scenarios) && result.scenarios.length ? result.scenarios : [{ id: "calculated", totals: result.totals, retirementProjection: projection, destination: result.destination }];
    const rows = [];
    if (record(projection.planningRange) && record(projection.planningRange.cases)) {
      ["favorable", "central", "adverse"].forEach(function (key) {
        const planningCase = projection.planningRange.cases[key];
        if (record(planningCase)) rows.push(["Current " + key + " planning case", planningCase.annualTaxReserve, null, null, null, planningCase.requiredCapital]);
      });
    } else if (projection.planningRange) rows.push(["Current broad planning estimate", null, null, null, null, projection.planningRange]);
    scenarios.forEach(function (scenario) {
      const property = record(scenario.destination) && record(scenario.destination.property) ? scenario.destination.property : record(result.destination) ? result.destination.property : null;
      const stages = record(property) && record(property.stages) ? property.stages : {};
      const propertyNotApplicable = record(property) && property.taxpayerScope === "not_applicable";
      const annualProperty = propertyNotApplicable ? { notApplicable: true } : record(stages.annual) ? stages.annual.nonTaxTotal : 0;
      const lifecycle = propertyNotApplicable ? { notApplicable: true } : record(property) && record(property.totals) ? Number(property.totals.nonTax || 0) - Number(annualProperty || 0) : 0;
      const retirement = record(scenario.retirementProjection) ? scenario.retirementProjection : projection;
      const capital = retirement.capitalRange || (retirement.refined && retirement.refined.totalNeededToday);
      rows.push([branchLabel(scenario), scenario.totals && scenario.totals.annualTax, scenario.totals && scenario.totals.afterTaxDependableIncome, annualProperty, lifecycle, capital]);
    });
    const sourceById = Object.fromEntries((sources || []).filter(record).map(function (source) { return [source.id, source]; }));
    const audit = (auditSections || []).flatMap(function (section) { return Array.isArray(section.lines) ? section.lines : []; }).map(function (line) {
      return '<article><h4>' + escapeHtml(line.label) + '</h4><p>' + auditValueText(line, currency) + " · " + escapeHtml(line.formula) + '</p><p class="hint">Assumptions: ' + escapeHtml((line.assumptions || []).join("; ") || "None") + ". Exclusions: " + escapeHtml((line.exclusions || []).join("; ") || "None") + ". Confidence: " + escapeHtml(line.confidence) + ". Tax year: " + escapeHtml(line.taxYear || result.taxYear) + ". Rules: " + escapeHtml((line.ruleIds || []).join(", ")) + ". Sources: " + sourceLinks(line.sourceIds, sourceById) + "</p></article>";
    }).join("");
    const propertyNote = rows.some(function (row) { return row.some(function (value) { return record(value) && value.notApplicable === true; }); }) ? '<p>Owned-property calculation not applicable; include renter municipal/housing fees in annual spending.</p>' : "";
    return '<div><div class="table-wrap"><table class="result-table"><caption>Reconciled tax, income, property costs and capital</caption><thead><tr><th scope="col">Calculated branch</th><th scope="col">Annual tax</th><th scope="col">After-tax dependable income</th><th scope="col">Annual property fees</th><th scope="col">Lifecycle registration fees</th><th scope="col">Capital needed today</th></tr></thead><tbody>' + rows.map(function (row) { return '<tr><th scope="row">' + escapeHtml(row[0]) + "</th>" + row.slice(1).map(function (value) { return "<td>" + (record(value) && value.notApplicable === true ? "N/A" : amountText(value, currency)) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>" + propertyNote + '<details><summary>Calculation details and official sources</summary>' + audit + "</details></div>";
  }

  function createController(options) {
    const state = { answers: {}, questions: Array.isArray(options && options.questions) ? options.questions.slice() : [] };
    let message = "";
    return {
      answer: function (fact, value) {
        const question = typeof fact === "string" ? state.questions.find(function (candidate) { return candidate.fact === fact; }) : null;
        if (!question) throw new TypeError("Answer must match an active material question");
        const accepted = question.acceptedValues;
        const valid = question.control === "number" && record(accepted)
          ? typeof value === "number" && Number.isFinite(value) && value >= accepted.min && value <= accepted.max && (accepted.integer !== true || Number.isInteger(value))
          : question.control === "date" && record(accepted)
            ? typeof value === "string" && value >= accepted.min && value <= accepted.max
            : Array.isArray(accepted) && accepted.some(function (candidate) { return candidate === value; });
        if (!valid) throw new TypeError("Answer is outside the active question contract");
        state.answers[fact] = value;
        message = "Tax estimate inputs updated in this browser only.";
      },
      snapshot: function () { return { answers: Object.assign({}, state.answers), questions: state.questions.slice() }; },
      announcement: function () { return message; },
    };
  }

  function coerceAnswer(question, value, checked) {
    if (question && question.control === "number") return value === "" ? null : Number(value);
    if (question && question.control === "checkbox") return checked === true;
    if (question && Array.isArray(question.acceptedValues) && question.acceptedValues.includes(true) && question.acceptedValues.includes(false)) return value === "true";
    return value;
  }

  function shouldHandlePlanningEvent(detailedForm, target) {
    return !(detailedForm && typeof detailedForm.contains === "function" && detailedForm.contains(target));
  }

  function nextPairQuestions(planningFacts, answers) {
    const has = function (fact) { return Object.prototype.hasOwnProperty.call(answers || {}, fact); };
    const option = function (value, label) { return { value: value, label: label }; };
    const yesNo = [option(false, "No"), option(true, "Yes")];
    const yesNoUnsure = [option("no", "No"), option("yes", "Yes"), option("not_sure", "Not sure")];
    const residence = [
      { id: "uae-days", fact: "daysInDestination", control: "number", label: "Days in the UAE during the relevant 12 months", reason: "This profile uses the official 183-day residence route.", acceptedValues: { min: 183, max: 365, step: 1, integer: true } },
      { id: "hong-kong-days", fact: "daysInHome", control: "number", label: "Days in Hong Kong during the tax year", reason: "The agreement tests the current year and either adjacent assessment year.", acceptedValues: { min: 0, max: 366, step: 1, integer: true } },
    ];
    let pending = residence.filter(function (question) { return !has(question.fact); });
    if (pending.length) return pending;
    if (Number(answers.daysInHome) <= 180 && !has("daysInHomePreviousYear")) return [{ id: "hong-kong-prior-days", fact: "daysInHomePreviousYear", control: "number", label: "Days in Hong Kong in the previous tax year", reason: "More than 300 days across the current and either adjacent assessment year establishes residence under the agreement.", acceptedValues: { min: 0, max: 366, step: 1, integer: true } }];
    if (Number(answers.daysInHome) <= 180 && Number(answers.daysInHome) + Number(answers.daysInHomePreviousYear) <= 300 && !has("followingYearDaysKnown")) return [{ id: "hong-kong-following-known", fact: "followingYearDaysKnown", control: "radio", label: "Can you give the Hong Kong days for the following tax year?", reason: "The following adjacent year can change the agreement's residence result; choose Not sure if it is future or uncertain.", acceptedValues: ["yes", "no", "not_sure"], options: [option("yes", "Yes"), option("no", "Not yet — future or unknown"), option("not_sure", "Not sure")] }];
    if (answers.followingYearDaysKnown === "yes" && !has("daysInHomeFollowingYear")) return [{ id: "hong-kong-following-days", fact: "daysInHomeFollowingYear", control: "number", label: "Days in Hong Kong in the following tax year", reason: "The agreement counts two consecutive assessment years when either one is the relevant year.", acceptedValues: { min: 0, max: 366, step: 1, integer: true } }];
    const dayOutcome = hongKongDomesticResidence(answers);
    if (dayOutcome === "incomplete" && Number(answers.daysInHome) <= 180 && answers.followingYearDaysKnown === "yes" && has("daysInHomeFollowingYear")) {
      pending = [
        { id: "hong-kong-settled-daily-life", fact: "hongKongSettledDailyLife", control: "radio", label: "Apart from temporary trips, was Hong Kong the place of your normal settled daily life?", reason: "IRD guidance looks at where a person habitually and normally lives for daily life; this asks for the fact, not a legal conclusion.", acceptedValues: ["no", "yes", "not_sure"], options: yesNoUnsure },
        { id: "hong-kong-fixed-home", fact: "hongKongFixedHome", control: "radio", label: "Did you keep a fixed home available in Hong Kong?", reason: "IRD lists a fixed Hong Kong residence as an objective ordinary-residence factor.", acceptedValues: ["no", "yes", "not_sure"], options: yesNoUnsure },
        { id: "hong-kong-work-business", fact: "hongKongWorkOrBusiness", control: "radio", label: "Did you work or run a business in Hong Kong?", reason: "IRD lists Hong Kong work or business as an objective ordinary-residence factor.", acceptedValues: ["no", "yes", "not_sure"], options: yesNoUnsure },
        { id: "hong-kong-close-family", fact: "hongKongCloseFamily", control: "radio", label: "Did your close family mainly live in Hong Kong?", reason: "IRD lists where family and relatives mainly live as an objective ordinary-residence factor.", acceptedValues: ["no", "yes", "not_sure"], options: yesNoUnsure },
      ].filter(function (question) { return !has(question.fact); });
      if (pending.length) return pending;
    }
    const domesticOutcome = hongKongDomesticResidence(answers);
    if (domesticOutcome !== "not_resident") return [];
    const eligibility = [
      { id: "hong-kong-source-income", fact: "hasHongKongSourceIncome", control: "radio", label: "Will any income come from Hong Kong services, business, property, or a Hong Kong pension fund?", reason: "Hong Kong taxes relevant Hong Kong-source income even for non-residents.", acceptedValues: [false, true], options: yesNo },
      { id: "hong-kong-property", fact: "hasHongKongProperty", control: "radio", label: "Will you keep any Hong Kong property?", reason: "A Hong Kong property needs its own complete property lifecycle calculation.", acceptedValues: [false, true], options: yesNo },
    ];
    const unansweredEligibility = eligibility.filter(function (question) { return !has(question.fact); });
    if (unansweredEligibility.length || eligibility.some(function (question) {
      return question.fact === "hasHongKongSourceIncome" && answers[question.fact] === true ||
        question.fact === "hasHongKongProperty" && answers[question.fact] === true;
    })) return unansweredEligibility;
    const money = function (id, fact, label, reason) { return { id: id, fact: fact, control: "number", label: label, reason: reason, acceptedValues: { min: 0, max: 1000000000, step: 1, integer: false } }; };
    const advanced = [
      { id: "retirement-account", fact: "retirementAccountClassification", control: "select", label: "What type of account funds the portfolio withdrawals?", reason: "This retired, nonworking profile supports ordinary personal investments, not employment income or retirement-scheme withdrawals.", acceptedValues: ["personal_investment", "hong_kong_retirement_scheme", "other_retirement_account"], options: [option("personal_investment", "Ordinary personal investments"), option("hong_kong_retirement_scheme", "Hong Kong MPF or retirement scheme"), option("other_retirement_account", "Another retirement account")] },
    ];
    if (Number(planningFacts && planningFacts.propertyPrice || 0) > 0) {
      advanced.push(
        { id: "financing-type", fact: "financingType", control: "radio", label: "How will you fund the Dubai purchase?", reason: "A mortgage adds registration and lender fees outside this narrow profile.", acceptedValues: ["cash", "mortgage"], options: [option("cash", "Cash purchase"), option("mortgage", "Mortgage or other property financing")] },
        { id: "property-type", fact: "propertyType", control: "select", label: "Dubai property type", reason: "The supported fixed map fee is for a villa or apartment.", acceptedValues: ["villa_or_apartment", "land_or_other"], options: [option("villa_or_apartment", "Villa or apartment"), option("land_or_other", "Land or another property type")] },
        money("service-charges", "annualServiceCharges", "Annual approved building service charges not included in living expenses", "Use the property-specific amount from the Dubai Land Department service-charge index. Enter zero if it is already in monthly living expenses."),
        money("housing-fee", "annualHousingFee", "Annual Dubai Municipality housing fee not included in living expenses", "Use the amount shown for the property by Dubai Municipality or DEWA. Enter zero if it is already in monthly living expenses."),
        { id: "exit-plan", fact: "exitPlan", control: "radio", label: "Which property transfer should this plan model?", reason: "Sale, gift and inheritance have different registration fees.", acceptedValues: ["keep", "sale", "gift", "inheritance"], options: [option("keep", "Keep the property"), option("sale", "Sell it"), option("gift", "Gift it to family"), option("inheritance", "Transfer it through inheritance")] }
      );
      if (answers.exitPlan === "gift") {
        advanced.push({ id: "gift-relationship", fact: "giftRelationship", control: "select", label: "Who would receive the gift?", reason: "The supported DLD gift route is limited to the stated qualifying relationships.", acceptedValues: ["first_degree_family", "other"], options: [option("first_degree_family", "Parent, child, or spouse"), option("other", "Someone else")] });
        advanced.push(money("gift-valuation", "expectedGiftValuation", "Expected DLD gift valuation in planning currency", "DLD calculates the gift registration fee from the property valuation, not the original purchase price."));
      }
      if (answers.exitPlan === "sale") advanced.push(money("sale-price", "expectedSalePrice", "Expected sale price in planning currency", "The seller registration fee is calculated from the sale value."));
    }
    return advanced.filter(function (question) { return !has(question.fact); });
  }

  function materialQuestions(bundle) {
    if (record(bundle) && record(bundle.residence_profile) && record(bundle.question_rules) && record(bundle.current_residence) && profileApi && typeof profileApi.nextQuestions === "function") {
      return profileApi.nextQuestions(bundle.residence_profile, bundle.question_rules, bundle.current_residence);
    }
    return record(bundle) && Array.isArray(bundle.questions) ? bundle.questions.slice() : [];
  }

  function runRefinement(input) {
    if (!record(input)) throw new TypeError("Detailed refinement input is required");
    if (record(input.uiPayload) && record(input.uiPayload.supported_profiles)) {
      if (!record(input.planningFacts)) throw new TypeError("Live planning facts are required");
      const eligibilityFacts = Object.assign({}, input.answers || {}, input.planningFacts, {
        giftValuationAed: Number(input.answers && input.answers.expectedGiftValuation || 0) * Number(input.planningFacts && input.planningFacts.aedPerCurrency || 0),
        dependableIncomeIndexingCompatible: input.planningFacts && input.planningFacts.dependableIncomeIndexingCompatible !== false,
        requireCompleteEligibility: true,
      });
      const access = profileAccess(input.destinationId, input.uiPayload, { homeJurisdictionId: input.homeJurisdictionId }, eligibilityFacts);
      if (!access.available) throw new TypeError(access.reason);
      if (!hkUaeApi || typeof hkUaeApi.buildRuntimeBundle !== "function") throw new TypeError("Live planning facts and the validated pair factory are required");
      if (!Number.isFinite(Number(input.planningFacts.aedPerCurrency)) || Number(input.planningFacts.aedPerCurrency) <= 0) throw new TypeError("A current AED conversion rate is required for official AED-denominated fees.");
      const remaining = nextPairQuestions(input.planningFacts, input.answers || {});
      if (remaining.length) throw new TypeError("Complete the remaining detailed tax questions before calculating.");
      const calculationProfile = buildDetailedProfile(access.definition, input.planningFacts, input.answers || {});
      calculationProfile.destination.property.aedPerCurrency = Number(input.planningFacts.aedPerCurrency);
      const runtime = hkUaeApi.buildRuntimeBundle(access.definition, calculationProfile, input.uiPayload.sources || []);
      const result = detailed.calculateDetailedTax(calculationProfile, runtime.rules);
      const audit = explain.explainCalculation(result);
      return { result: result, audit: audit, markup: '<h3>' + escapeHtml(access.definition.label) + "</h3>" + resultMarkup(result, audit, input.uiPayload.sources || []) };
    }
    const access = jurisdictionAccess(input.destinationId, input.uiPayload, { homeJurisdictionId: input.homeJurisdictionId });
    if (!access.available) throw new TypeError(access.reason);
    const bundle = access.bundle;
    if (!record(bundle.profile) || !record(bundle.rules) || !detailed || !explain) throw new TypeError("Complete detailed calculation dependencies are required");
    const calculationProfile = JSON.parse(JSON.stringify(bundle.profile));
    Object.assign(calculationProfile.residence, record(input.answers) ? input.answers : {});
    const result = detailed.calculateDetailedTax(calculationProfile, bundle.rules);
    const audit = explain.explainCalculation(result);
    return { result: result, audit: audit, markup: resultMarkup(result, audit, input.uiPayload.sources || []) };
  }

  function initDetailedTaxUI(formId, payload) {
    if (typeof document === "undefined") return null;
    const form = document.getElementById(formId);
    const destination = document.getElementById("ret-destination");
    const home = document.getElementById("ret-home-tax-jurisdiction");
    const homeField = document.getElementById("ret-home-tax-jurisdiction-field");
    const button = document.getElementById("ret-tax-refine");
    const section = document.getElementById("ret-tax-detailed");
    const detailedForm = document.getElementById("ret-tax-detailed-form");
    const questions = document.getElementById("ret-tax-detailed-questions");
    const resultContainer = document.getElementById("ret-tax-detailed-result");
    const status = document.getElementById("ret-tax-detailed-status");
    const availability = document.getElementById("ret-tax-detailed-availability");
    if (!form || !destination || !home || !homeField || !button || !section || !detailedForm || !questions || !resultContainer || !status || !availability) return null;
    let answers = {};
    let active = false;
    const field = function (id) { return document.getElementById(id); };
    const number = function (id) {
      const control = field(id);
      const cleaned = control ? String(control.value || "").replace(/[^0-9.-]/g, "") : "";
      const value = Number(cleaned);
      return Number.isFinite(value) ? value : 0;
    };
    function planningFacts() {
      const currency = field("ret-currency") ? field("ret-currency").value : "USD";
      const rates = record(payload.planning_currencies) && record(payload.planning_currencies.rates_to_usd) ? payload.planning_currencies.rates_to_usd : {};
      const housingPlan = field("ret-housing-plan") ? field("ret-housing-plan").value : "rent";
      const buysProperty = housingPlan === "buy_now" || housingPlan === "buy_retirement";
      const propertyPrice = buysProperty ? number("ret-property-budget") : 0;
      const dependable = [
        { amount: number("ret-pension"), indexed: field("ret-pension-indexed") && field("ret-pension-indexed").checked },
        { amount: number("ret-other-income"), indexed: field("ret-other-indexed") && field("ret-other-indexed").checked },
        { amount: number("ret-rental-income"), indexed: field("ret-rental-indexed") && field("ret-rental-indexed").checked },
      ].filter(function (item) { return item.amount > 0; });
      const indexChoices = Array.from(new Set(dependable.map(function (item) { return item.indexed === true; })));
      let planningRange = null;
      try {
        const parsed = JSON.parse(button.dataset.planningCases || "null");
        if (record(parsed) && record(parsed.cases)) planningRange = parsed;
      } catch (error) {
        planningRange = null;
      }
      return {
        currency: currency,
        currentAge: number("ret-current-age"), retirementAge: number("ret-retirement-age"), horizonYears: number("ret-horizon"),
        annualSpending: number("ret-monthly-spending") * 12,
        annualPension: number("ret-pension"), annualOtherIncome: number("ret-other-income"), annualRentalIncome: number("ret-rental-income"),
        annualWithdrawals: number("ret-tax-withdrawals"), propertyPrice: propertyPrice, housingPlan: housingPlan,
        propertyUse: field("ret-tax-property-use") ? field("ret-tax-property-use").value : "personal",
        selectedAfterTaxReturn: number("ret-expected-return") / 100,
        explicitReturnProvided: !!(field("ret-expected-return") && String(field("ret-expected-return").value).trim()),
        monthlyIncomeBeforeRetirement: number("ret-monthly-income"), incomeInvestedRate: number("ret-income-invested-rate") / 100,
        generalInflation: number("ret-general-inflation") / 100, propertyInflation: number("ret-property-inflation") / 100,
        emergencyReserveMonths: number("ret-reserve-months"), hasLiveDependableIncome: dependable.length > 0,
        dependableIncomeIndexed: indexChoices.length === 1 && indexChoices[0] === true,
        dependableIncomeIndexingCompatible: indexChoices.length <= 1,
        aedPerCurrency: Number(rates[currency]) * Number(payload.aed_per_usd),
        planningRange: planningRange,
      };
    }
    let answerCurrency = planningFacts().currency;
    function access(facts) { return profileAccess(destination.value, payload, { homeJurisdictionId: home.value }, facts); }
    function supportedHomes() {
      return Object.keys(payload.supported_profiles || {}).map(function (id) { return payload.supported_profiles[id]; }).filter(function (item) {
        return record(item) && item.detailed_enabled === true && item.synthetic === false && item.destination_id === destination.value;
      });
    }
    function resetResult() {
      resultContainer.hidden = true;
      resultContainer.innerHTML = "";
    }
    function resetIfCurrencyChanged() {
      const nextCurrency = planningFacts().currency;
      if (nextCurrency === answerCurrency) return false;
      answerCurrency = nextCurrency;
      answers = {};
      active = false;
      resetResult();
      questions.innerHTML = "";
      section.hidden = true;
      status.textContent = "Detailed monetary answers were cleared because the planning currency changed.";
      return true;
    }
    function renderQuestions() {
      const currentQuestions = nextPairQuestions(planningFacts(), answers);
      questions.innerHTML = currentQuestions.map(questionMarkup).join("");
      const facts = Object.assign({}, planningFacts(), answers, { propertyPriceAed: planningFacts().propertyPrice * planningFacts().aedPerCurrency });
      const current = access(facts);
      const submit = detailedForm.querySelector('[type="submit"]');
      if (!current.available) {
        status.textContent = current.reason;
        if (submit) submit.disabled = true;
      } else {
        status.textContent = currentQuestions.length ? "Answer the remaining facts that can change this estimate." : "All material facts are ready. Calculate the exact profile.";
        if (submit) submit.disabled = currentQuestions.length > 0;
        if (!currentQuestions.length) {
          try {
            runRefinement({ destinationId: destination.value, homeJurisdictionId: home.value, uiPayload: payload, planningFacts: planningFacts(), answers: answers });
          } catch (error) {
            status.textContent = error instanceof Error ? error.message : "The complete profile could not be executed.";
            if (submit) submit.disabled = true;
          }
        }
      }
      return currentQuestions;
    }
    function sync() {
      const pairs = supportedHomes();
      homeField.hidden = pairs.length === 0;
      Array.from(home.options).forEach(function (option) {
        if (!option.value) return;
        option.hidden = !pairs.some(function (pair) { return pair.home_jurisdiction_id === option.value; });
        option.disabled = option.hidden;
      });
      if (home.selectedOptions && home.selectedOptions[0] && home.selectedOptions[0].disabled) home.value = "";
      const current = access(planningFacts());
      button.dataset.detailedAvailable = current.available ? "true" : "false";
      button.hidden = !current.available;
      button.disabled = !current.available;
      availability.textContent = current.available ? "Exact destination-and-home refinement is available for this profile." : current.reason;
      if (!current.available) { section.hidden = true; active = false; }
      if (active && current.available) { resetResult(); renderQuestions(); }
    }
    destination.addEventListener("change", sync);
    home.addEventListener("change", sync);
    button.addEventListener("click", function () {
      const current = access(planningFacts());
      if (!current.available) return;
      answers = {};
      active = true;
      resetResult();
      section.hidden = false;
      renderQuestions();
      const first = questions.querySelector("input, select");
      if (first && typeof first.focus === "function") first.focus();
    });
    questions.addEventListener("change", function (event) {
      const control = event.target;
      const currentQuestions = nextPairQuestions(planningFacts(), answers);
      const question = currentQuestions.find(function (candidate) { return candidate.fact === control.name; });
      if (!question || (question.control === "radio" && !control.checked)) return;
      try {
        const controller = createController({ questions: currentQuestions });
        controller.answer(question.fact, coerceAnswer(question, control.value, control.checked));
        answers[question.fact] = controller.snapshot().answers[question.fact];
      } catch (error) {
        status.textContent = error instanceof Error ? error.message : "Check the detailed tax answers.";
        return;
      }
      resetResult();
      renderQuestions();
    });
    detailedForm.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!detailedForm.checkValidity()) return;
      try {
        const output = runRefinement({ destinationId: destination.value, homeJurisdictionId: home.value, uiPayload: payload, planningFacts: planningFacts(), answers: answers });
        resultContainer.innerHTML = output.markup;
        resultContainer.hidden = false;
        status.textContent = "Exact destination-and-home calculation updated from the current plan.";
      } catch (error) {
        resetResult();
        status.textContent = error instanceof Error ? error.message : "This exact calculation is unavailable for the current facts.";
      }
    });
    form.addEventListener("input", function (event) { if (!shouldHandlePlanningEvent(detailedForm, event.target)) return; if (resetIfCurrencyChanged()) { sync(); return; } if (active) { resetResult(); renderQuestions(); } else sync(); });
    form.addEventListener("change", function (event) { if (!shouldHandlePlanningEvent(detailedForm, event.target)) return; resetIfCurrencyChanged(); sync(); });
    sync();
    return { sync: sync, planningFacts: planningFacts, answers: function () { return Object.assign({}, answers); } };
  }

  return {
    profileAccess: profileAccess,
    buildDetailedProfile: buildDetailedProfile,
    jurisdictionAccess: jurisdictionAccess,
    questionMarkup: questionMarkup,
    resultMarkup: resultMarkup,
    createController: createController,
    coerceAnswer: coerceAnswer,
    shouldHandlePlanningEvent: shouldHandlePlanningEvent,
    hongKongDomesticResidence: hongKongDomesticResidence,
    nextPairQuestions: nextPairQuestions,
    materialQuestions: materialQuestions,
    runRefinement: runRefinement,
    initDetailedTaxUI: initDetailedTaxUI,
  };
});
