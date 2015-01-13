/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');

var app = new EmberApp();

// Use `app.import` to add additional libraries to the generated
// output files.
//
// If you need to use different assets in different
// environments, specify an object as the first parameter. That
// object's keys should be the environment name and the values
// should be the asset to use in that environment.
//
// If the library that you are including contains AMD or ES6
// modules that you would like to import into your application
// please specify an object with the list of modules as keys
// along with the exports of each module as its value.

app.import('bower_components/modernizr/modernizr.js');
app.import('bower_components/foundation/js/foundation.js');
app.import('bower_components/markdown/lib/markdown.js');
app.import('bower_components/moment/moment.js');
app.import('bower_components/javascript-linkify/ba-linkify.min.js');
app.import('bower_components/growl/javascripts/jquery.growl.js');
app.import('bower_components/growl/stylesheets/jquery.growl.css');
app.import('bower_components/datetimepicker/jquery.datetimepicker.js');
app.import('bower_components/datetimepicker/jquery.datetimepicker.css');
app.import('bower_components/fontawesome/css/font-awesome.css');
app.import('bower_components/ember-data-tastypie-adapter/dist/global/ember-data-tastypie-adapter.js');
app.import('bower_components/raven-js/dist/raven.js');
app.import('bower_components/fastclick/lib/fastclick.js');
app.import('bower_components/chardin.js/chardinjs.js');
app.import('bower_components/chardin.js/chardinjs.css');
app.import('vendor/touchwipe/jquery.touchwipe.1.1.1.js');
app.import('bower_components/jquery.hotkeys/jquery.hotkeys.js');

/* Fontawesome Fonts */
app.import('bower_components/fontawesome/fonts/fontawesome-webfont.woff', {
        destDir: 'fonts/'
    }
);
app.import('bower_components/fontawesome/fonts/fontawesome-webfont.ttf', {
        destDir: 'fonts/'
    }
);
app.import('bower_components/fontawesome/fonts/fontawesome-webfont.svg', {
        destDir: 'fonts/'
    }
);
app.import('bower_components/fontawesome/fonts/fontawesome-webfont.eot', {
        destDir: 'fonts/'
    }
);

module.exports = app.toTree();
