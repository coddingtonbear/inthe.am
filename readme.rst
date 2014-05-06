Inthe.AM
========

.. image:: https://travis-ci.org/coddingtonbear/inthe.am.png?branch=master
   :target: https://travis-ci.org/coddingtonbear/inthe.am

Released under the `GNU AFFERO GENERAL PUBLIC LICENSE <http://www.gnu.org/licenses/agpl-3.0-standalone.html>`_.

`File issues and bug reports on Github <https://github.com/coddingtonbear/inthe.am/issues>`_.

Questions?  Ask in ``##inthe.am`` on `Freenode <http://freenode.net/irc_servers.shtml>`_.

Setting up a Development Environment
------------------------------------

.. image:: https://travis-ci.org/coddingtonbear/inthe.am.png?branch=development
   :target: https://travis-ci.org/coddingtonbear/inthe.am

1. Create the virtual machine ``vagrant up``
2. Enter the virtual machine: ``vagrant ssh``
3. Switch to the project directory: ``cd /var/www/twweb/``
4. Start the ``runserver`` by running ``python manage.py runserver 0.0.0.0:8000``


Compile the Templates, CSS, and Javascript Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Development Environment Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Various environment variables are set in ``environment_variables.sh``,
  and you will need to set *at least* the following two environment variables
  to use the site; see `Google OAuth Keys`_ for details regarding what you
  should set these variables to:

  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``

* "When trying to start ``runserver``, I get a message reading
  'Error: That port is already in use.'".

  * While a browser window is open, one connection is persistently
    held open for streaming data from the server to the client as
    it has changed; this process will not close until it lost its
    connection with the browser.  Either close your browser tab
    showing that window or find the PID of the still-running process
    using ``ps -f``, and killing the running process with ``kill <that pid>``.

* "When running tests with ``python manage.py test taskmanager``, it isn't
  seeing changes I've made."

  * Tests are ran against production (read: uglified) assets rather than
    the assets that are simply concatenated.  Make sure that you have ran
    ``grunt uglify`` before running tests.

Google OAuth Keys
~~~~~~~~~~~~~~~~~

Follow the following steps to generate Google OAuth credentials to use for
development and testing.  These are used for the log-in process, and are
functionally essential for doing much of anything with Inthe.AM.

1. Go to `Google's developer console <https://console.developers.google.com/project>`_.
2. Create a new project.
3. From within your project, create a new "Client ID" by going to
   "APIs & Auth" > "Credentials" and clicking on the "Create New Client ID"
   button.
4. Select "Web Application"
5. Enter the following for 'Authorized Javascript Origins'::

    http://127.0.0.1
    http://localhost

6. Enter the following for 'Authorized Redirect URI'::

    http://127.0.0.1:8000/complete/google-oauth2/
    http://localhost:8081/complete/google-oauth2/

7. Save
8. You will be presented with your newly-generated client ID.
9. Enter the value of "Client ID" into your ``environment_variables.sh``
   as the value of the ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``.
10. Enter the value of "Client Secret" into your ``environment_variables.sh``
    as the value of the ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``.
11. If you are currently running an existing ``runserver`` session, you will
    want to close it, run ``source environment_variables.sh`` to update your
    environment with the environment variables you've set, and start the
    ``runserver`` once again.

