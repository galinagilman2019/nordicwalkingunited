"use strict";

const { series } = require("gulp");
const setProduction = require("./environment");  // Import the environment task
const local = require("./local");                // Import local task
const { revisionCssTask, replaceRevvedCssTask } = require("./revisioning");  // Import revisioning tasks
const styles = require("./styles");              // Import styles task

const buildTask = series(setProduction, local, revisionCssTask, replaceRevvedCssTask, styles);

module.exports = buildTask;  // Export the build task


