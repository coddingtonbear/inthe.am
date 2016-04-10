var EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
    var app = new EmberApp(defaults, {
      sourcemaps: ['js'],
      sassOptions: {
          sourceMap: true,
      },
      fingerprint: {
          exclude: [
              'apple',
              'colorschemes',
              'static',
              'logo.png',
          ],
      }
    });

    app.import('bower_components/modernizr/modernizr.js');
    app.import('bower_components/foundation/js/foundation.js');
    app.import('bower_components/markdown/lib/markdown.js');
    app.import('bower_components/moment/moment.js');
    app.import('bower_components/javascript-linkify/ba-linkify.min.js');
    app.import('bower_components/growl/javascripts/jquery.growl.js');
    app.import('bower_components/growl/stylesheets/jquery.growl.css');
    app.import('bower_components/datetimepicker/jquery.datetimepicker.js');
    app.import('bower_components/datetimepicker/jquery.datetimepicker.css');
    app.import('bower_components/raven-js/dist/raven.js');
    app.import('bower_components/raven-js/dist/plugins/ember.js');
    app.import('bower_components/fastclick/lib/fastclick.js');
    app.import('bower_components/chardin.js/chardinjs.js');
    app.import('bower_components/chardin.js/chardinjs.css');
    app.import('bower_components/Sortable/Sortable.js');
    app.import('vendor/touchwipe/jquery.touchwipe.1.1.1.js');
    app.import('bower_components/jquery.hotkeys/jquery.hotkeys.js');

    return app.toTree();
};
