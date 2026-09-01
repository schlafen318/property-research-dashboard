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

  function money(value) {
    return value === null || value === undefined
      ? "—"
      : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
  }

  function label(value) {
    const labels = {
      likely_nonresident: "Likely nonresident",
      residence_depends_on_days_and_ties: "Depends on days and ties",
      likely_resident: "Likely resident",
      straightforward: "Straightforward",
      moderate: "Moderate",
      complex: "Complex",
      highly_profile_dependent: "Highly profile-dependent",
      likely_eligible: "Likely eligible",
    };
    return labels[value] || String(value || "").replaceAll("_", " ");
  }

  function textElement(tag, value) {
    const element = document.createElement(tag);
    element.textContent = value;
    return element;
  }

  function renderRows(rows, profile, tbody) {
    const fragments = rows.map(function (row) {
      const tr = document.createElement("tr");
      const heading = textElement("th", row.name);
      heading.scope = "row";
      heading.appendChild(textElement("small", row.country));
      tr.appendChild(heading);
      if (!row.rankable) {
        const pending = document.createElement("td");
        pending.colSpan = 6;
        if (row.tax.status === "tax_impact_unavailable") {
          pending.appendChild(textElement("strong", "Research pending — tax evidence is incomplete, so this destination is not ranked."));
        } else {
          pending.appendChild(textElement("strong", "Eligibility check needed — " + row.eligibility.summary));
        }
        tr.appendChild(pending);
        return tr;
      }
      tr.appendChild(textElement("td", row.overall_score.toFixed(2) + "/5"));
      const eligibility = textElement("td", label(row.eligibility.status));
      eligibility.appendChild(textElement("small", row.eligibility.summary));
      tr.appendChild(eligibility);
      const residence = textElement("td", label(row.tax.residence_outcome));
      residence.appendChild(textElement("small", row.tax.scope_summary));
      residence.appendChild(textElement("small", "Watch: " + (row.tax.warnings || []).join(" ")));
      tr.appendChild(residence);
      const readiness = textElement("td", label(row.tax.readiness));
      readiness.appendChild(textElement("small", String(row.tax.confidence).replaceAll("_", "-") + " confidence"));
      tr.appendChild(readiness);
      const reserve = textElement("td", money(row.budget.central_tax_reserve));
      reserve.appendChild(textElement("small", money(row.budget.favorable_tax_reserve) + "–" + money(row.budget.adverse_tax_reserve)));
      tr.appendChild(reserve);
      const action = document.createElement("td");
      const link = textElement("a", "Build your plan");
      link.href = safeCalculatorHref({
        destinationId: row.destination_id,
        household: profile.household,
        housing: profile.housing,
      });
      action.appendChild(link);
      tr.appendChild(action);
      return tr;
    });
    tbody.replaceChildren.apply(tbody, fragments);
  }

  function initFireAbroad(rootId) {
    const element = typeof document === "undefined" ? null : document.getElementById(rootId);
    if (!element) return false;
    const dataElement = document.getElementById("fire-abroad-data");
    const tbody = document.getElementById("fire-results-body");
    if (!dataElement || !tbody || typeof GHAFireAbroad === "undefined") return false;
    const payload = JSON.parse(dataElement.textContent);
    const controls = {
      stay: document.getElementById("fire-stay"),
      days: document.getElementById("fire-days"),
      income: document.getElementById("fire-income"),
      housing: document.getElementById("fire-housing"),
      propertyUse: document.getElementById("fire-property-use"),
      mobility: document.getElementById("fire-mobility"),
      taxHome: document.getElementById("fire-tax-home"),
    };
    const propertyGroup = document.querySelector('[data-fire-group="property-use"]');
    function update() {
      const profile = {
        stay_mode: controls.stay.value,
        annual_day_band: controls.days.value,
        funding_source: controls.income.value,
        housing: controls.housing.value,
        property_use: controls.propertyUse.value,
        mobility_rights: controls.mobility.value,
        home_tax_context: controls.taxHome.value,
        household: "single",
        tax_mode: "destination_estimate",
      };
      const visibility = taxControlVisibility({
        housing: profile.housing,
        taxMode: profile.tax_mode,
        wealthTaxRelevant: false,
      });
      propertyGroup.hidden = !visibility.propertyUse;
      const rows = GHAFireAbroad.rankDestinations({
        destinations: payload.destinations,
        retirementCosts: payload.retirementCosts,
        firePayload: payload.fire,
        profile: profile,
      });
      renderRows(rows, profile, tbody);
    }
    Object.keys(controls).forEach(function (key) {
      controls[key].addEventListener("change", update);
    });
    update();
    return true;
  }

  return {
    taxControlVisibility: taxControlVisibility,
    safeCalculatorHref: safeCalculatorHref,
    initFireAbroad: initFireAbroad,
  };
});
