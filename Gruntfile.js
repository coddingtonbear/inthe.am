var STATIC_ROOT = 'inthe_am/taskmanager/static/sources/';
var STATIC_FILES = [
  'raven.min.js',
  'jquery.min.js',
  'jquery.datetimepicker.js',
  'jquery.growl.js',
  'jquery.touchwipe.min.js',
  'fastclick.js',
  'moment.min.js',
  'markdown.min.js',
  'handlebars-v1.3.0.js',
  'ember.min.js',  // Will be replaced by ember.js in dev
  'ember-data.min.js',  // Will be replaced by ember-data.js in dev
  'tastypie_adapter.js',
  'templates.js',
  'task_manager.js',
  'foundation.min.js',
];
var STATIC_COLLECTED_DEV = STATIC_ROOT + '../compiled.dev.js';
var STATIC_COLLECTED_PROD = STATIC_ROOT + '../compiled.min.js';

var getStaticFiles = function(dev) {
  actual_files = [];
  for(var i=0; i<STATIC_FILES.length; i++) {
    var filename = STATIC_FILES[i];
    if(dev && filename.indexOf('ember') > -1) {
      filename = filename.replace('.min', '');
    }
    actual_files.push(
      STATIC_ROOT + filename
    );
  }
  return actual_files;
};

var CONFIG = {
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
    devel: {
      src: [],
      dest: null,
      nonull: true,
    }
  },
  uglify: {
    options: {
      mangle: false,
      sourceMap: true,
    },
    dist: {
      files: {}
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
    concat: {
      files: [
        STATIC_ROOT + '*.js'
      ],
      tasks: [
        'concat'
      ]
    }
  },
};
CONFIG.concat.devel.src = getStaticFiles(true);
CONFIG.concat.devel.dest = STATIC_COLLECTED_DEV;
CONFIG.uglify.dist.files[STATIC_COLLECTED_PROD] = getStaticFiles(false);

module.exports = function(grunt){
  CONFIG.pkg = grunt.file.readJSON('package.json');
  grunt.initConfig(CONFIG);
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-ember-handlebars');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
};
