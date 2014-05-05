var STATIC_ROOT = 'inthe_am/taskmanager/static/sources/';

module.exports = function(grunt){
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    browserify: {
      dist: {
        files: {
          'inthe_am/taskmanager/static/sources/task_manager.js': [
              'ember_modules/*.js'
          ]
        },
        options: {
        }
      }
    },
    ember_handlebars: {
      compile: {
        options: {
          processName: function(name) {
            return name.substr(
              name.lastIndexOf('/') + 1,
              name.lastIndexOf('.') - name.lastIndexOf('/') - 1
            ).replace('__', '/');
          }
        },
        files: {
          'inthe_am/taskmanager/static/sources/templates.js': [
            'handlebars_templates/*.hbs'
          ]
        }
      }
    },
    sass: {
      options: {
        includePaths: [
          'inthe_am/taskmanager/static/foundation/bower_components/foundation/scss'
        ]
      },
      dist: {
        options: {
          'outputStyle': 'compressed'
        },
        files: {
          'inthe_am/taskmanager/static/colorschemes/light-16.theme.css': 'inthe_am/taskmanager/static/colorschemes/light-16.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-16.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-16.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/light-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/light-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-red-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-red-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-green-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-green-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-blue-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-blue-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-violets-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-violets-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-yellow-green.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-yellow-green.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/dark-gray-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/dark-gray-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/solarized-dark-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/solarized-dark-256.theme.scss',
          'inthe_am/taskmanager/static/colorschemes/solarized-light-256.theme.css': 'inthe_am/taskmanager/static/colorschemes/solarized-light-256.theme.scss',
          'inthe_am/taskmanager/static/app.css': 'inthe_am/taskmanager/static/foundation/scss/app.scss',
        }
      }
    },
    concat: {
      options: {
        separator: ';',
      },
      dist: {
        src: [
          STATIC_ROOT + 'raven.min.js',
          STATIC_ROOT + 'jquery.min.js',
          STATIC_ROOT + 'jquery.datetimepicker.js',
          STATIC_ROOT + 'jquery.growl.js',
          STATIC_ROOT + 'jquery.touchwipe.min.js',
          STATIC_ROOT + 'fastclick.js',
          STATIC_ROOT + 'moment.min.js',
          STATIC_ROOT + 'markdown.min.js',
          STATIC_ROOT + 'handlebars-v1.3.0.js',

          STATIC_ROOT + 'ember.min.js',
          STATIC_ROOT + 'ember-data.min.js',

          STATIC_ROOT + 'tastypie_adapter.js',
          STATIC_ROOT + 'templates.js',
          STATIC_ROOT + 'task_manager.js',
          STATIC_ROOT + 'foundation.min.js',
        ],
        dest: STATIC_ROOT + '../compiled.js',
        nonull: true,
      },
      devel: {
        src: [
          STATIC_ROOT + 'raven.min.js',
          STATIC_ROOT + 'jquery.min.js',
          STATIC_ROOT + 'jquery.datetimepicker.js',
          STATIC_ROOT + 'jquery.growl.js',
          STATIC_ROOT + 'jquery.touchwipe.min.js',
          STATIC_ROOT + 'fastclick.js',
          STATIC_ROOT + 'moment.min.js',
          STATIC_ROOT + 'markdown.min.js',
          STATIC_ROOT + 'handlebars-v1.3.0.js',

          STATIC_ROOT + 'ember.js',
          STATIC_ROOT + 'ember-data.js',

          STATIC_ROOT + 'tastypie_adapter.js',
          STATIC_ROOT + 'templates.js',
          STATIC_ROOT + 'task_manager.js',
          STATIC_ROOT + 'foundation.min.js',
        ],
        dest: STATIC_ROOT + '../compiled-devel.js',
        nonull: true,
      },
    },
    watch: {
      sass: {
        files: [
          'inthe_am/taskmanager/static/**/*.scss',
          'inthe_am/taskmanager/static/colorschemes/*.scss',
        ],
        tasks: [
          'sass'
        ]
      },
      jscript: {
        files: [
          'ember_modules/**/*.js',
        ],
        tasks: [
          'browserify'
        ]
      },
      handlebars: {
        files: [
          'handlebars_templates/**/*.hbs'
        ],
        tasks: [
          'ember_handlebars',
        ]
      },
      concatenation: {
        files: [
          STATIC_ROOT + '*.js'
        ],
        tasks: [
          'concat'
        ]
      }
    },
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-ember-handlebars');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-concat');
};
