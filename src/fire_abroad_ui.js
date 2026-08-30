(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.GHAFireAbroadUI = api;
})(typeof self !== "undefined" ? self : this, function (root) {
  "use strict";

  const DESTINATION_SLUG = /^[a-z0-9-]+$/;
  const HOUSEHOLDS = new Set(["single", "couple"]);
  const HOUSING = new Set(["rent", "own", "buy_now", "buy_retirement"]);
  const STAY_MODES = new Set(["seasonal", "part_year", "full_relocation"]);
  const ACTIVITY_PRIORITIES = new Set(["balanced", "walking", "cycling", "hiking", "water", "winter_sports", "fitness_social"]);
  const EVENT_NAMES = new Set([
    "page_view", "stay_mode_change", "activity_filter_use", "destination_guide_click", "calculator_handoff",
  ]);

  function object(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value) ? value : {};
  }

  function safeDestinationId(value) {
    const destinationId = typeof value === "string" ? value : "";
    return DESTINATION_SLUG.test(destinationId) ? destinationId : "";
  }

  function safeCalculatorHref(input) {
    const value = object(input);
    const profile = object(value.profile);
    const destinationId = safeDestinationId(value.destinationId);
    const household = HOUSEHOLDS.has(profile.household) ? profile.household : "single";
    const housing = HOUSING.has(profile.housing) ? profile.housing : "rent";
    return "/retirement-abroad-calculator/?destination=" + encodeURIComponent(destinationId) +
      "&household=" + encodeURIComponent(household) + "&housing=" + encodeURIComponent(housing);
  }

  function safeAnalyticsPayload(eventName, details) {
    if (!EVENT_NAMES.has(eventName)) return null;
    const source = object(details);
    const payload = { eventName: eventName };
    if (eventName === "stay_mode_change" && STAY_MODES.has(source.stayMode)) payload.stayMode = source.stayMode;
    if (eventName === "activity_filter_use" && ACTIVITY_PRIORITIES.has(source.activityPriority)) {
      payload.activityPriority = source.activityPriority;
    }
    if (eventName === "destination_guide_click" || eventName === "calculator_handoff") {
      const destinationId = safeDestinationId(source.destinationId);
      if (destinationId) payload.destinationId = destinationId;
    }
    return payload;
  }

  function resultRowsForDisplay(results, activityPriority) {
    const rows = Array.isArray(results) ? results.slice() : [];
    if (!ACTIVITY_PRIORITIES.has(activityPriority) || activityPriority === "balanced") return rows;
    const matchingRanked = [];
    const unranked = [];
    rows.forEach(function (row) {
      const tags = Array.isArray(row && row.activity_tags) ? row.activity_tags : [];
      const rankable = row && typeof row.score === "number" && (row.status === "eligible" || row.status === "conditional");
      if (!rankable) unranked.push(row);
      else if (tags.includes(activityPriority)) matchingRanked.push(row);
    });
    return matchingRanked.concat(unranked);
  }

  function initFireAbroad(appRoot) {
    const host = appRoot || root;
    const documentRoot = host && host.document;
    const engine = host && host.GHAFireAbroad;
    if (!documentRoot || !engine || typeof engine.normalizeProfile !== "function" || typeof engine.rankDestinations !== "function") return;
    const dataNode = documentRoot.getElementById("fire-abroad-data");
    const form = documentRoot.getElementById("fire-abroad-form");
    const resultsNode = documentRoot.getElementById("fire-results");
    const summaryNode = documentRoot.getElementById("fire-results-summary");
    if (!dataNode || !form || !resultsNode) return;
    let payload;
    try {
      payload = JSON.parse(dataNode.textContent || "{}");
    } catch (error) {
      if (summaryNode) summaryNode.textContent = "Results could not be updated because the destination data is unavailable.";
      return;
    }
    if (form.dataset.fireAbroadBound === "true") return;
    form.dataset.fireAbroadBound = "true";

    function element(id) {
      return documentRoot.getElementById(id);
    }

    function readProfile() {
      const raw = {};
      const controls = {
        stay_mode: "fire-stay-mode",
        age: "fire-age",
        household: "fire-household",
        housing: "fire-housing",
        mobility_rights: "fire-mobility-rights",
        home_tax_context: "fire-home-tax-context",
        annual_days: "fire-annual-days",
        income_type: "fire-income-type",
        activity_priority: "fire-activity-priority",
      };
      Object.keys(controls).forEach(function (key) {
        const control = element(controls[key]);
        if (!control) return;
        raw[key] = key === "age" || key === "annual_days" ? Number(control.value) : control.value;
      });
      return engine.normalizeProfile(raw);
    }

    function appendText(parent, tagName, value) {
      const node = documentRoot.createElement(tagName);
      node.textContent = value;
      parent.appendChild(node);
      return node;
    }

    function track(eventName, details) {
      const event = safeAnalyticsPayload(eventName, details);
      if (event && host.GHA && typeof host.GHA.track === "function") host.GHA.track(event.eventName, event);
    }

    function render(profile) {
      const rows = resultRowsForDisplay(engine.rankDestinations(payload, profile), profile.activity_priority);
      resultsNode.replaceChildren();
      rows.forEach(function (row) {
        const article = documentRoot.createElement("article");
        appendText(article, "h2", row.name);
        appendText(article, "p", "Eligibility: " + String(row.status || "needs_verification") + ". " + String(row.status_reason || ""));
        appendText(article, "p", row.score === null ? "Ranking: Unranked until evidence is verified." : "FIRE Abroad score: " + row.score.toFixed(2) + " out of 5.");
        if (row.strongest_activity_reason) appendText(article, "p", row.strongest_activity_reason);
        (Array.isArray(row.warnings) ? row.warnings : []).forEach(function (warning) {
          appendText(article, "p", "Warning: " + String(warning));
        });
        const calculator = documentRoot.createElement("a");
        calculator.href = safeCalculatorHref({ destinationId: row.destination_id, profile: profile });
        calculator.textContent = "Explore retirement budget";
        calculator.addEventListener("click", function () {
          track("calculator_handoff", { destinationId: row.destination_id });
        });
        article.appendChild(calculator);
        const guide = documentRoot.createElement("a");
        const destinationId = safeDestinationId(row.destination_id);
        guide.href = destinationId ? "/destinations/" + encodeURIComponent(destinationId) + "/" : "/destinations/";
        guide.textContent = "Read destination guide";
        guide.addEventListener("click", function () {
          track("destination_guide_click", { destinationId: row.destination_id });
        });
        article.appendChild(documentRoot.createTextNode(" "));
        article.appendChild(guide);
        resultsNode.appendChild(article);
      });
      if (summaryNode) {
        const ranked = rows.filter(function (row) { return typeof row.score === "number"; }).length;
        const unranked = rows.length - ranked;
        summaryNode.textContent = ranked + " ranked destinations" + (unranked ? "; " + unranked + " need verification." : ".");
      }
    }

    function update(event) {
      if (event) event.preventDefault();
      const profile = readProfile();
      render(profile);
      const stayMode = element("fire-stay-mode");
      const activity = element("fire-activity-priority");
      if (event && event.type === "change" && event.target === stayMode) track("stay_mode_change", { stayMode: profile.stay_mode });
      if (event && event.type === "change" && event.target === activity) {
        track("activity_filter_use", { activityPriority: profile.activity_priority });
      }
    }

    form.addEventListener("submit", update);
    form.addEventListener("change", update);
    render(readProfile());
    track("page_view", {});
  }

  return { safeCalculatorHref, safeAnalyticsPayload, resultRowsForDisplay, initFireAbroad };
});
