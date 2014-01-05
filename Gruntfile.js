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
    watch: {
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
  //grunt.loadNpmTasks('grunt-ember-templates');
  grunt.loadNpmTasks('grunt-ember-handlebars');

};
