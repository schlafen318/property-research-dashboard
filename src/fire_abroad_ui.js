(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFireAbroadUI = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  function taxControlVisibility(input) {
    const housing = String(input && input.housing || "rent");
    const estimated = String(input && input.taxMode || "destination_estimate") === "destination_estimate";
    const buys = housing === "buy_now" || housing === "buy_retirement" || housing === "own";
    return {
      propertyUse: estimated && buys,
      wealthBand: estimated && Boolean(input && input.wealthTaxRelevant),
      planningInputs: estimated,
    };
  }

  function safeSlug(value, fallback) {
    const slug = String(value || "");
    return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) ? slug : fallback;
  }

  function safeCalculatorHref(input) {
    const destination = safeSlug(input && input.destinationId, "fukuoka-itoshima");
    const household = input && input.household === "couple" ? "couple" : "single";
    const allowedHousing = new Set(["rent", "own", "buy_now", "buy_retirement"]);
    const housing = allowedHousing.has(input && input.housing) ? input.housing : "rent";
    return "/retirement-abroad-calculator/?destination=" + encodeURIComponent(destination) +
      "&household=" + household + "&housing=" + housing;
  }

  function initFireAbroad(rootId) {
    const element = typeof document === "undefined" ? null : document.getElementById(rootId);
    if (!element) return false;
    return true;
  }

  return {
    taxControlVisibility: taxControlVisibility,
    safeCalculatorHref: safeCalculatorHref,
    initFireAbroad: initFireAbroad,
  };
});
