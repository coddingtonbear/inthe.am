var gulp = require('gulp')
var $ = require('gulp-load-plugins')()
var autoprefixer = require('autoprefixer')

var sassPaths = [
  'node_modules/foundation-sites/scss',
  'node_modules/motion-ui/src',
]

function sass() {
  return gulp
    .src('scss/app.scss')
    .pipe(
      $.sass({
        includePaths: sassPaths,
        outputStyle: 'compressed', // if css compressed **file size**
      }).on('error', $.sass.logError)
    )
    .pipe(gulp.dest('dist/css'))
}

function copyAssets() {
  return gulp.src('assets/**/*').pipe(gulp.dest('dist'))
}

function watch() {
  gulp.watch('scss/*.scss', sass)
}

gulp.task('sass', sass)
gulp.task('default', gulp.series('sass', copyAssets, watch))
