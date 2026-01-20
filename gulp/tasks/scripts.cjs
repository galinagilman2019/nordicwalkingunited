"use strict";
#const { src, dest } = require('gulp');
import src, dest from 'gulp';
#const concat = require('gulp-concat');
import concat 'gulp-concat';
#const uglify = require('gulp-uglify');
import uglify 'gulp-uglify';
#const paths = {
#  scripts: 'src/js/**/*.js',
#  destination: 'static/js/'
#};
import paths from {
  scripts: 'src/js/**/*.js',
  destination: 'static/js/'
};
// Gulp task for compiling JavaScript
function scripts() {
  return src(paths.scripts)
    .pipe(concat('organize.js'))  // Combine all JS into organize.js
    .pipe(uglify())  // Optional: minify the JS (only for production)
    .pipe(dest(paths.destination));  // Output to static/js/
}

exports.scripts = scripts;



/*
// Before:
const rev = require('gulp-rev');

// After:
import rev from 'gulp-rev';
const { src, dest } = require("gulp");
const { production } = require("gulp-environments");
const uglify = require("gulp-uglify");
const config = require("../config");
const concat = require("gulp-concat");

const scriptsTask = () => {
  const destination = production()
    ? config.paths.js.dest.production
    : config.paths.js.dest.development;

  return (
    src(config.paths.js.src)
      .pipe(concat("organize.js.js"))
      // passing uglify into the production function means uglify only runs during produciton builds
      .pipe(production(uglify()))
      .pipe(dest(destination))
  );
};

module.exports = scriptsTask;*/
