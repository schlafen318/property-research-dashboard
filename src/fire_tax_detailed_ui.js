(function (root, factory) {
  const detailed = typeof module === "object" && module.exports ? require("./fire_tax_detailed.js") : root && root.GHAFireTaxDetailed;
  const explain = typeof module === "object" && module.exports ? require("./fire_tax_explain.js") : root && root.GHAFireTaxExplain;
  const profile = typeof module === "object" && module.exports ? require("./fire_tax_profile.js") : root && root.GHAFireTaxProfile;
  const api = factory(detailed, explain, profile);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireTaxDetailedUI = api;
})(typeof window !== "undefined" ? window : null, function (detailed, explain, profileApi) {
  "use strict";

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function escapeHtml(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function jurisdictionAccess(destinationId, payload, profile) {
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
      if (question.control === "select") {
        control = '<select id="' + escapeHtml(id) + '" name="' + escapeHtml(question.fact) + '" aria-describedby="' + escapeHtml(helpId) + '" required><option value="">Choose one</option>' + accepted.map(function (value) { return '<option value="' + escapeHtml(value) + '">' + escapeHtml(value) + "</option>"; }).join("") + "</select>";
      } else {
        control = accepted.map(function (value, index) {
          const optionId = id + "-" + index;
          return '<label for="' + escapeHtml(optionId) + '"><input id="' + escapeHtml(optionId) + '" type="radio" name="' + escapeHtml(question.fact) + '" value="' + escapeHtml(value) + '" aria-describedby="' + escapeHtml(helpId) + '"' + (index === 0 ? " required" : "") + '> ' + escapeHtml(value) + "</label>";
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

  function resultMarkup(result, auditSections, sources) {
    if (!record(result) || !record(result.totals)) return '<p role="status" aria-live="polite">A refined result is not available.</p>';
    const currency = result.currency || "";
    const projection = record(result.retirementProjection) ? result.retirementProjection : {};
    const rows = [
      ["Annual tax", result.totals.annualTax],
      ["One-time property taxes", result.totals.oneTimeTaxes],
      ["Gross dependable income", result.totals.grossDependableIncome],
      ["After-tax dependable income", result.totals.afterTaxDependableIncome],
      ["Planning range", projection.planningRange],
      ["Refined range", projection.capitalRange || (projection.refined && projection.refined.totalNeededToday)],
    ];
    const sourceById = Object.fromEntries((sources || []).filter(record).map(function (source) { return [source.id, source]; }));
    const branchText = (result.scenarios || []).map(function (scenario) {
      return '<li><strong>' + escapeHtml(scenario.id) + ":</strong> " + amountText(scenario.totals && scenario.totals.annualTax, currency) + " annual tax</li>";
    }).join("");
    const audit = (auditSections || []).flatMap(function (section) { return Array.isArray(section.lines) ? section.lines : []; }).map(function (line) {
      return '<article><h4>' + escapeHtml(line.label) + '</h4><p>' + amountText(line.value, currency) + " · " + escapeHtml(line.formula) + '</p><p class="hint">Assumptions: ' + escapeHtml((line.assumptions || []).join("; ") || "None") + ". Exclusions: " + escapeHtml((line.exclusions || []).join("; ") || "None") + ". Confidence: " + escapeHtml(line.confidence) + ". Tax year: " + escapeHtml(line.taxYear || result.taxYear) + ". Rules: " + escapeHtml((line.ruleIds || []).join(", ")) + ". Sources: " + sourceLinks(line.sourceIds, sourceById) + "</p></article>";
    }).join("");
    return '<div><table class="result-table"><caption>Reconciled tax and retirement calculation</caption><thead><tr><th scope="col">Line</th><th scope="col">Amount</th></tr></thead><tbody>' + rows.map(function (row) { return '<tr><th scope="row">' + escapeHtml(row[0]) + "</th><td>" + amountText(row[1], currency) + "</td></tr>"; }).join("") + "</tbody></table>" + (branchText ? '<h3>Calculated branches</h3><ul>' + branchText + "</ul>" : "") + '<details><summary>Calculation details and official sources</summary>' + audit + "</details></div>";
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
    return value;
  }

  function materialQuestions(bundle) {
    if (record(bundle) && record(bundle.residence_profile) && record(bundle.question_rules) && record(bundle.current_residence) && profileApi && typeof profileApi.nextQuestions === "function") {
      return profileApi.nextQuestions(bundle.residence_profile, bundle.question_rules, bundle.current_residence);
    }
    return record(bundle) && Array.isArray(bundle.questions) ? bundle.questions.slice() : [];
  }

  function runRefinement(input) {
    if (!record(input)) throw new TypeError("Detailed refinement input is required");
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
    const button = document.getElementById("ret-tax-refine");
    const section = document.getElementById("ret-tax-detailed");
    const questions = document.getElementById("ret-tax-detailed-questions");
    const resultContainer = document.getElementById("ret-tax-detailed-result");
    const status = document.getElementById("ret-tax-detailed-status");
    const availability = document.getElementById("ret-tax-detailed-availability");
    if (!form || !destination || !button || !section || !questions || !resultContainer || !status || !availability) return null;
    let controller = null;
    function access() { return jurisdictionAccess(destination.value, payload, { homeJurisdictionId: form.dataset.homeTaxJurisdiction || "" }); }
    function sync() {
      const current = access();
      button.dataset.detailedAvailable = current.available ? "true" : "false";
      button.hidden = !current.available;
      button.disabled = !current.available;
      availability.textContent = current.available ? "Exact destination-and-home refinement is available for this profile." : current.reason;
      if (!current.available) section.hidden = true;
    }
    destination.addEventListener("change", sync);
    button.addEventListener("click", function () {
      const current = access();
      if (!current.available) return;
      const bundle = current.bundle;
      const activeQuestions = materialQuestions(bundle);
      controller = createController({ questions: activeQuestions });
      questions.innerHTML = activeQuestions.map(questionMarkup).join("");
      section.hidden = false;
      status.textContent = activeQuestions.length ? "Answer only the facts that can change this estimate." : "No further material questions are needed.";
    });
    form.addEventListener("submit", function () {
      const current = access();
      if (!current.available || !controller || !record(current.bundle.profile) || !detailed || !explain) return;
      const bundle = current.bundle;
      const activeQuestions = materialQuestions(bundle);
      try {
        activeQuestions.forEach(function (question) {
          const selector = '[name="' + String(question.fact).replace(/(["\\])/g, "\\$1") + '"]';
          const controls = Array.from(questions.querySelectorAll(selector));
          const control = question.control === "radio" ? controls.find(function (item) { return item.checked; }) : controls[0];
          if (!control) return;
          controller.answer(question.fact, coerceAnswer(question, control.value, control.checked));
        });
      } catch (error) {
        status.textContent = error instanceof Error ? error.message : "Check the detailed tax answers.";
        return;
      }
      const profile = JSON.parse(JSON.stringify(bundle.profile));
      Object.assign(profile.residence, controller.snapshot().answers);
      const result = detailed.calculateDetailedTax(profile, bundle.rules);
      resultContainer.innerHTML = resultMarkup(result, explain.explainCalculation(result), payload.sources || []);
      status.textContent = "Refined tax estimate updated.";
    });
    sync();
    return { sync: sync };
  }

  return {
    jurisdictionAccess: jurisdictionAccess,
    questionMarkup: questionMarkup,
    resultMarkup: resultMarkup,
    createController: createController,
    coerceAnswer: coerceAnswer,
    materialQuestions: materialQuestions,
    runRefinement: runRefinement,
    initDetailedTaxUI: initDetailedTaxUI,
  };
});
