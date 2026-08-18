(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.GHARetirementRankingTable = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function sortRankingRows(rows, key, direction) {
    const factor = direction === "descending" ? -1 : 1;
    return rows.slice().sort(function (left, right) {
      let comparison;
      if (key === "name") {
        comparison = String(left.name).localeCompare(String(right.name), undefined, {
          sensitivity: "base",
        });
      } else {
        comparison = Number(left[key]) - Number(right[key]);
      }
      return comparison === 0 ? Number(left.rank) - Number(right.rank) : comparison * factor;
    });
  }

  function initRetirementRankingTable(rootElement) {
    if (!rootElement) return;
    const visibleBody = rootElement.querySelector("[data-ranking-visible]");
    const additionalBody = rootElement.querySelector("[data-ranking-additional]");
    const buttons = Array.from(rootElement.querySelectorAll("[data-sort-key]"));
    if (!visibleBody || !additionalBody || buttons.length === 0) return;

    const rows = Array.from(rootElement.querySelectorAll(".ranking-row")).map(function (element) {
      return {
        element: element,
        rank: Number(element.dataset.rank),
        name: element.dataset.name,
        annual: Number(element.dataset.annual),
        savings: Number(element.dataset.savings),
        property: Number(element.dataset.property),
      };
    });
    let activeKey = "savings";
    let activeDirection = "ascending";

    function render(key, direction) {
      const sorted = sortRankingRows(rows, key, direction);
      sorted.slice(0, 10).forEach(function (row) { visibleBody.appendChild(row.element); });
      sorted.slice(10).forEach(function (row) { additionalBody.appendChild(row.element); });
      rootElement.querySelectorAll("thead th").forEach(function (header) {
        header.setAttribute("aria-sort", "none");
      });
      buttons.forEach(function (button) {
        const selected = button.dataset.sortKey === key;
        const indicator = button.querySelector(".sort-indicator");
        button.closest("th").setAttribute("aria-sort", selected ? direction : "none");
        if (indicator) indicator.textContent = selected ? (direction === "ascending" ? "↑" : "↓") : "↕";
      });
      activeKey = key;
      activeDirection = direction;
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        const key = button.dataset.sortKey;
        const direction = key === activeKey && activeDirection === "ascending" ? "descending" : "ascending";
        render(key, direction);
      });
    });
    render(activeKey, activeDirection);
  }

  return {
    sortRankingRows: sortRankingRows,
    initRetirementRankingTable: initRetirementRankingTable,
  };
});
