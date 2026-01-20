import gulp from 'gulp';

// Import individual tasks
import { build } from './gulp/tasks/build.js';
import { clean } from './gulp/tasks/clean.js';
import { copy } from './gulp/tasks/copy.js';
import { environment } from './gulp/tasks/environment.js';
import { local } from './gulp/tasks/local.js';
import { revisioning } from './gulp/tasks/revisioning.js';
import { scripts } from './gulp/tasks/scripts.js';
import { styles } from './gulp/tasks/styles.js';
import { watch } from './gulp/tasks/watch.js';  // Import watch task

// Export the tasks
export { clean, copy, environment, local, revisioning, scripts, styles, watch };

// Default task - running build and watch together
export const defaultTask = gulp.series(build, watch);

// Watch task - runs scripts and styles on file changes
export const watchTask = gulp.series(scripts, styles, watch);

// Build task - runs all necessary tasks in series
export const fullBuild = gulp.series(clean, scripts, styles, revisioning, copy);

// Export the tasks you want to run with `gulp` from the command line
export const dev = gulp.series(defaultTask, watchTask);



