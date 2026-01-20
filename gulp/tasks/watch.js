"use strict";
import gulp from 'gulp';  // Use import instead of require
import { series } from 'gulp';  // Import the necessary tasks or functions

// Define your tasks or import them if they are in other files
import { local, styles } from './tasks';  // Make sure to import the tasks you need

// Watch for changes and run appropriate tasks
const watchTask = () => {
  gulp.watch("src/js/**/*.js", series(local));  // Example watch for JS changes
  gulp.watch("src/css/**/*.css", series(styles));  // Example watch for CSS changes
};

// Export the watch task
export default watchTask;





