
Compile the Templates, CSS, and Javascript Modules
==================================================

Templates and Javascript modules are managed by `Grunt <http://gruntjs.com/>`_,
and changes you make to the Handlebars
templates (``handlebars_templates/*.hbs``), Javascript modules
(``ember_modules/**/*.js``), and SCSS files
(``inthe_am/taskmanager/static/colorschemes/*.scss`` and 
``inthe_am/taskmanager/static/foundation/scss/*.scss``) will not be visible
until you have first compiled them into their web-native formats, and, in the
case of Javscript files, concatenated together into a single file for
delivery to the browser.

Luckily, you do not need to do this manually; Grunt can run in the background
while you perform your edits so that you need not manually compile the templates
after each modification.  You can do that by first installing grunt and the
relevant modules from the *host* *enviroment*::

    npm install
    npm install -g grunt-cli

Once the above have installed successfully, you can run the grunt watcher
by simply running::

    grunt watch

.. note::

   You should run `grunt watch` from the host environment rather than installing
   and running grunt from within your VM.  The functionality used by grunt
   for determining if files have changed is much less efficient when run
   within the VM due to the way files are shared between the host and VM.

If you by chance would like to compile the templates and Javascript files just
once, you can run the command::

    grunt ember_handlebars sass browserify concat

