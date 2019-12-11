const gulp = require("gulp");
const minify = require("gulp-minify");

gulp.task('minify', () => {
  return gulp.src('main/static/main/js/convert.js', { allowEmpty: true }) 
    .pipe(minify({noSource: true}))
    .pipe(gulp.dest('main/static/main/js'))
})

gulp.task('default', gulp.series(['minify']));