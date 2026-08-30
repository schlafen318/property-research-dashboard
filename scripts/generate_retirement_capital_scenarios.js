"use strict";

const fs = require("fs");
const path = require("path");
const finder = require(path.join(__dirname, "..", "src", "retirement_destination_finder.js"));

try {
  const input = JSON.parse(fs.readFileSync(0, "utf8"));
  if (!Array.isArray(input.capitalValues) || !input.baseInput) {
    throw new Error("Capital values and base input are required");
  }
  const output = {};
  input.capitalValues.forEach(function (value) {
    const capital = Number(value);
    if (!Number.isFinite(capital) || capital < 0) throw new Error("Capital value must be non-negative");
    output[String(capital)] = finder.recommendProjectedCapital(Object.assign({}, input.baseInput, {
      projectedCapitalUsd: capital,
    }));
  });
  process.stdout.write(JSON.stringify(output));
} catch (error) {
  process.stderr.write((error && error.message || "Scenario generation failed") + "\n");
  process.exitCode = 1;
}
