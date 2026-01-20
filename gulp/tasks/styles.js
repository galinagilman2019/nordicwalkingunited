"use strict";
import { src, dest, series } from "gulp";
import sass from "gulp-sass";
import gulpEnvironments from "gulp-environments";
const { production } = gulpEnvironments;

import concat from "gulp-concat";
import cleanCSS from "gulp-clean-css"; // Minify CSS
import autoprefixer from "gulp-autoprefixer"; // Add vendor prefixes
import config from "../config.mjs";

// Task to process and compile Sass files
const sassTask = () => {
  const compress = production();
  return src(config.paths.css.src)
    .pipe(sass({ outputStyle: compress ? 'compressed' : 'expanded' }).on('error', sass.logError))
    .pipe(autoprefixer()) // Add vendor prefixes
    .pipe(compress ? cleanCSS() : dest('.')) // Minify CSS in production
    .pipe(dest(config.paths.temp)); // Save to temporary directory
};

// Task to bundle multiple CSS files into one
const bundleTasks = Object.entries(config.paths.css.bundles).map(
  ([key, paths]) => {
    const bundleTask = () => {
      const destination = production()
        ? config.paths.css.dest.production
        : config.paths.css.dest.development;

      return src(paths)
        .pipe(concat(`${key}.css`)) // Concatenate CSS files
        .pipe(dest(destination)); // Save the bundled file
    };

    Object.defineProperty(bundleTask, "name", {
      value: `styles:${key}`,
      writable: false,
    });

    return bundleTask;
  }
);

export default series(sassTask, ...bundleTasks);

/*const { src, dest, series } = require("gulp");
const stylus = require("gulp-stylus");
const { production } = require("gulp-environments");
const concat = require("gulp-concat");

const config = require("../config");

const stylusTask = () => {
  const compress = production();
  return src(config.paths.css.src)
    .pipe(stylus({ compress }))
    .pipe(dest(config.paths.temp));  // Outputs processed styles to temp folder
};

// Create dynamic tasks for each CSS bundle
const tasks = [stylusTask];

for (const key in config.paths.css.bundles) {
  const func = () => {
    const destination = production()
      ? config.paths.css.dest.production
      : config.paths.css.dest.development;

    return src(config.paths.css.bundles[key])
      .pipe(concat(`${key}.css`))  // Concatenate bundled CSS
      .pipe(dest(destination));    // Output to the correct destination
  };

  // Give each dynamic task a unique name for debugging
  Object.defineProperty(func, "name", {
    value: `styles:${key}`,
    writable: false,
  });

  tasks.push(func);  // Add dynamic task to tasks array
}


module.exports = series(...tasks);  // Export all tasks as a series*/
