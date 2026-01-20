"use strict";
const { src, dest } = require("gulp");

// Define the local task
const local = () => {
  return src("src/js/*.js")  // Adjust path as needed
    .pipe(dest("dist/js/"));  // Adjust path as needed
};

module.exports = local;  // Export the local task
