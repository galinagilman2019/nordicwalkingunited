module.exports = {
  paths: {
    project: './',
    css: {
      src: [
        './static/source/css/*.styl',
        '!./static/source/css/common.styl'
      ],
      dest: {
        production: './static/build/css/',
        development: './static/local/css/',
      },
      bundles: {
        global: [
          './node_modules/bootstrap/dist/css/bootstrap.min.css',
          './static/source/vendor/css/sss.css',
          './temp/global.css'
        ],
        event: [
          './node_modules/bootstrap/dist/css/bootstrap.min.css',
          './temp/event.css'
        ],
        admin: [
          './temp/admin.css'
        ]
      }
    },
    js: {
      src: [
        './static/source/js/*.js'  // Keep this as it is to include all JS files
      ],
      dest: {
        production: './static/build/js/', // Change this path to static/js
        development: './static/local/js/',  // Keep local development path
      }
    },
    copy: {
      src: [
        './static/source/**',
        '!./static/source/css/',
        '!./static/source/css/**',
        '!./static/source/js/',
        '!./static/source/js/**'
      ],
      dest: {
        production: './static/build/',
        development: './static/local/',
      }
    },
    manifest: './static/',
    revisioning: ['./static/build/css/*.css', './static/build/js/*.js'],
    temp: './temp/'
  }
};
