(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHAFindYourFitUI = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";

  function settingScore(goalScore, locationTypes, settings) {
    if (settings.includes("any")) return goalScore;
    return locationTypes.some(function (setting) { return settings.includes(setting); }) ? 5 : 2;
  }

  function matchingSettings(locationTypes, settings) {
    return settings.filter(function (setting) { return locationTypes.includes(setting); });
  }

  function syncSettingInputs(inputs, changedInput) {
    const noPreference = inputs.find(function (input) { return input.value === "any"; });
    if (!noPreference) return;
    if (changedInput === noPreference && changedInput.checked) {
      inputs.filter(function (input) { return input !== noPreference; }).forEach(function (input) {
        input.checked = false;
      });
    } else if (changedInput !== noPreference && changedInput.checked) {
      noPreference.checked = false;
    }
    if (!inputs.some(function (input) { return input.checked; })) noPreference.checked = true;
  }

  function initSettingInputs(inputs) {
    inputs.forEach(function (input) {
      input.addEventListener("change", function () { syncSettingInputs(inputs, input); });
    });
  }

  return {
    initSettingInputs: initSettingInputs,
    matchingSettings: matchingSettings,
    settingScore: settingScore,
  };
});
