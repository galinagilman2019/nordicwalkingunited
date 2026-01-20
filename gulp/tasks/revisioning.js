"use strict";
import gulp from 'gulp';
import rev from 'gulp-rev';
import gulpRevCSS from 'gulp-rev-css-url';
import fs from 'fs';
import path from 'path';
import config from '../config.mjs';

const revisioningTask = async () => {
  const prodDir = config.paths.copy.dest.production;

  if (!fs.existsSync(prodDir)) {
    fs.mkdirSync(prodDir, { recursive: true });
  }

  return gulp.src(config.paths.revisioning, {
    base: prodDir,
    allowEmpty: true,
  })
    .pipe(rev())  // Use gulp-rev instead of gulp-rev-napkin
    .pipe(gulpRevCSS())
    .pipe(gulp.dest(prodDir))
    .pipe(rev.manifest())
    .pipe(gulp.dest(config.paths.manifest));
};

export { revisioningTask };




/*
import { src, dest } from "gulp";
import rev from "gulp-rev";
import revNapkin from "gulp-rev-napkin";
import revCSS from "gulp-rev-css-url";
import fs from "fs";
import path from "path";
import config from "../config.mjs";


const revisioningTask = async () => {
  const prodDir = config.paths.copy.dest.production;

  // Ensure the build/prod directory exists
  if (!fs.existsSync(prodDir)) {
    fs.mkdirSync(prodDir, { recursive: true });
  }

  return src(config.paths.revisioning, {
    base: prodDir,
    allowEmpty: true, // avoids crashing if directory is momentarily empty
  })
    .pipe(rev())
    .pipe(revCSS())
    .pipe(dest(prodDir))
    .pipe(revNapkin({ verbose: false }))
    .pipe(rev.manifest())
    .pipe(dest(config.paths.manifest));
};

export default revisioningTask;

/*const { src, dest } = require("gulp");
const rev = require("gulp-rev");  // Ensure gulp-rev is correctly imported
const revReplace = require("gulp-rev-replace");
const cleanCSS = require("gulp-clean-css");  // Optional: For CSS minification

// Task to revision CSS files
const revisionCssTask = () => {
  console.log("Running revisionCssTask...");

  return src("static/css/*.css")  // Adjust path as needed
    .pipe(rev())  // Ensure rev() is being used here correctly
    .pipe(cleanCSS())  // Optional: Minify CSS
    .pipe(dest("static/build/css/"))
    .pipe(rev.manifest())  // Generate a revision manifest
    .pipe(dest("static/build/css/"));  // Write manifest to build folder
};

// Task to replace the revisioned URLs in CSS
const replaceRevvedCssTask = () => {
  const manifest = src("static/build/css/rev-manifest.json");
  return src("static/css/*.css")  // Adjust path as needed
    .pipe(revReplace({ manifest: manifest }))  // Replace URLs in CSS
    .pipe(dest("static/build/css/"));
};

module.exports = { revisionCssTask, replaceRevvedCssTask };  // Export tasks*/
