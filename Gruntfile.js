module.exports = function(grunt){
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    browserify: {
      dist: {
        files: {
          'inthe_am/taskmanager/static/task_manager.js': [
              'inthe_am/taskmanager/static/modules/*.js'
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
          'inthe_am/taskmanager/static/templates.js': [
            'inthe_am/taskmanager/static/modules/templates/*.hbs'
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
          'inthe_am/taskmanager/static/modules/**/*.js',
        ],
        tasks: [
          'browserify'
        ]
      },
      handlebars: {
        files: [
          'inthe_am/taskmanager/static/modules/**/*.hbs'
        ],
        tasks: [
          'ember_handlebars',
        ]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-ember-handlebars');
  grunt.loadNpmTasks('grunt-sass');

};
