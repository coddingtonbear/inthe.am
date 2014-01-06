module.exports = function(grunt){
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    browserify: {
      dist: {
        files: {
          'twweb/taskmanager/static/task_manager.js': [
              'twweb/taskmanager/static/modules/*.js'
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
          'twweb/taskmanager/static/templates.js': [
            'twweb/taskmanager/static/modules/templates/*.hbs'
          ]
        }
      }
    },
    sass: {
      dist: {
        files: {
          'twweb/taskmanager/static/main.css': 'twweb/taskmanager/static/scss/main.scss'
        }
      }
    },
    watch: {
      sass: {
        files: [
          'twweb/taskmanager/static/scss/*.scss',
        ],
        tasks: [
          'sass'
        ]
      },
      jscript: {
        files: [
          'twweb/taskmanager/static/modules/**/*.js',
        ],
        tasks: [
          'browserify'
        ]
      },
      handlebars: {
        files: [
          'twweb/taskmanager/static/modules/**/*.hbs'
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
