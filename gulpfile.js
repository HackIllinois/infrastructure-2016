// set up gulp and packages
var gulp = require('gulp');
var sass = require('gulp-sass');
var min = require('gulp-minify-css');
var concat = require('gulp-concat');
var concatCSS = require('gulp-concat-css');
var uglify = require('gulp-uglify');
var del = require('del');

var DEV_SCSS = './dev/assets/styles/sass/**/*.scss';
var DEV_CORE_JS = './dev/assets/js/**/*.js';

var JS_BUNDLES = {
  // the vendor files are given explicitly so that they are concatenated
  // in the proper order
  'vendor_main': ['./dev/assets/js/vendor/jquery.min.js',
    './dev/assets/js/vendor/jquery-ui-easings.min.js',
    './dev/assets/js/vendor/modernizr.min.js',
    './dev/assets/js/vendor/parsley.min.js',
    './dev/assets/js/vendor/selectize.min.js',
    './dev/assets/js/vendor/moment.min.js'],
  'vendor_admin': ['./dev/assets/js/vendor/jquery.min.js',
    './dev/assets/js/vendor/jquery-ui-easings.min.js',
    './dev/assets/js/vendor/modernizr.min.js',
    './dev/assets/js/vendor/parsley.min.js',
    './dev/assets/js/vendor/bootstrap.min.js',
    './dev/assets/js/vendor/data-tables.min.js',
    './dev/assets/js/vendor/moment.min.js',
    './dev/assets/js/vendor/moment-timezone.min.js',
    './dev/assets/js/vendor/dymo.min.js'],
  'common': './dev/assets/js/common/**/*.js',
  'index': ['./dev/assets/js/index/**/*.js', '!./dev/assets/js/index/**/audio.js'], // audio is apparently not done
  'auth': './dev/assets/js/auth/**/*.js',
  'register': './dev/assets/js/register/**/*.js',
  'rsvp': './dev/assets/js/rsvp/**/*.js',
  'external': './dev/assets/js/external/**/*.js', // random external pages that ended up here
  'admin_review': './dev/assets/js/admin/review/*.js',
  'admin_review_details': './dev/assets/js/admin/review_details/*.js',
  'admin_checkin': './dev/assets/js/admin/checkin/*.js',
  'admin_checkin_details': './dev/assets/js/admin/checkin_details/*.js',
  'admin_users': './dev/assets/js/admin/users/*.js',
  'admin_user_details': './dev/assets/js/admin/user_details/*.js',
  'admin_network': './dev/assets/js/admin/network/*.js',
  'admin_notify': './dev/assets/js/admin/notify/*.js',
  'hardware': './dev/assets/js/hardware/*.js'
};
var SCSS_BUNDLES = {
  'archive': './dev/assets/styles/sass/archive.scss',
  'main': './dev/assets/styles/sass/main.scss',
  'admin': './dev/assets/styles/sass/admin.scss',
  'external': './dev/assets/styles/sass/external.scss' // random external pages that ended up here
};

var ALL_FONTS = './dev/assets/fonts/**/*';
var ALL_IMG = './dev/assets/img/**/**';
var ALL_AUDIO = './dev/assets/audio/**';
var ALL_FILES = './dev/files/**';

var DIST = './dist';
var DIST_JS = './dist/assets/js/';
var DIST_CSS = './dist/assets/css/';
var DIST_FONTS = './dist/assets/fonts/';
var DIST_IMG = './dist/assets/img/';
var DIST_AUDIO = './dist/assets/audio/';
var DIST_FILES = './dist/files/';

var WATCHING = [DEV_SCSS, DEV_CORE_JS];

function createJsBundleStream (bundle) {
  return gulp.src(JS_BUNDLES[bundle])
    .pipe(concat(bundle + '.min.js'));
}

function createCssBundleStream (bundle) {
  return gulp.src(SCSS_BUNDLES[bundle])
    .pipe(sass.sync())
    .pipe(concatCSS(bundle + '.min.css'));
}

gulp.task('clean', function(cb) {
  return del(DIST, cb);
});

gulp.task('copy:fonts', ['clean'], function () {
  gulp.src(ALL_FONTS)
    .pipe(gulp.dest(DIST_FONTS));
});

gulp.task('copy:img', ['clean'], function () {
  gulp.src(ALL_IMG)
    .pipe(gulp.dest(DIST_IMG));
});

gulp.task('copy:audio', ['clean'], function () {
  gulp.src(ALL_AUDIO)
    .pipe(gulp.dest(DIST_AUDIO));
});

gulp.task('copy:files', ['clean'], function () {
  gulp.src(ALL_FILES)
    .pipe(gulp.dest(DIST_FILES));
});

gulp.task('sass', ['clean'], function () {
  for (var bundle in SCSS_BUNDLES) {
    createCssBundleStream(bundle)
    .pipe(gulp.dest(DIST_CSS));
  }

});

gulp.task('sass:min', ['clean'], function () {
  for (var bundle in SCSS_BUNDLES) {
    createCssBundleStream(bundle)
    .pipe(min())
    .pipe(gulp.dest(DIST_CSS));
  }
});

gulp.task('js', ['clean'], function() {
  for (var bundle in JS_BUNDLES) {
    var stream = createJsBundleStream(bundle);
    stream.pipe(gulp.dest(DIST_JS));
  }
});

gulp.task('js:min', ['clean'], function () {
  for (var bundle in JS_BUNDLES) {
    var stream = createJsBundleStream(bundle);
    // do not mangle the vendor files, since these declare
    // global variables that we use elsewhere
    stream.pipe(uglify({ 'mangle': bundle !== 'vendor' }))
      .pipe(gulp.dest(DIST_JS));
  }
});

gulp.task('watch', ['copy', 'compile'], function() {
  gulp.watch(WATCHING, ['copy', 'compile']);
});

gulp.task('watch:min', ['copy', 'compile:min'], function() {
  gulp.watch(WATCHING, ['copy', 'compile:min']);
});

gulp.task('copy', ['copy:fonts', 'copy:img', 'copy:audio', 'copy:files']);

gulp.task('compile', ['sass', 'js']);
gulp.task('compile:min', ['sass:min', 'js:min']);

gulp.task('build:deploy', ['copy', 'compile:min']);

gulp.task('dev', ['watch']);
gulp.task('dev:min', ['watch:min']);
