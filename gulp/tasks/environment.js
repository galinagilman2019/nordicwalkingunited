"use strict";

const { production, current } = require("gulp-environments");
const log = require("fancy-log");

/**
 * Sets a global production marker that other tasks can read
 */
const setProduction = () => {
  console.log("Setting up production environment...");

  // If there is any asynchronous task, return a Promise or use 'done' to signal completion.
  // Since there are no async tasks here, we return a resolved Promise
  return Promise.resolve();
};

module.exports = setProduction;
