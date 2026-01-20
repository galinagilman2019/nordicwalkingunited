"use strict";

const del = require("del");

const clean = () => {
  return del(["dist/**", "build/**"]);  // Clean up the dist and build folders
};

module.exports = clean;  // Export the clean task

