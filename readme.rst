Inthe.AM
========

.. image:: https://travis-ci.org/coddingtonbear/inthe.am.png?branch=master
   :target: https://travis-ci.org/coddingtonbear/inthe.am

Released under the `GNU AFFERO GENERAL PUBLIC LICENSE <http://www.gnu.org/licenses/agpl-3.0-standalone.html>`_.

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
and in the development environment, changes you make to the Handlebars
templates (``handlebars_templates/*.hbs``), Javascript modules
(``ember_modules/**/*.js``), and SCSS files
(``inthe_am/taskmanager/static/colorschemes/*.scss`` and 
``inthe_am/taskmanager/static/foundation/scss/*.scss``) are compiled into their
respective web-native formats automatically by a service named ``taskd-grunt``.

If you by chance would like to compile the templates manually, you can run
the command::

    grunt ember_handlebars sass browserify

That having been said, you may want to stop the ``taskd-grunt`` service first
by running::

    sudo service taskd-grunt stop

.. note::

   For best results, it is recommended that you run the grunt watcher
   on the host environment.  Filesystem accesses from your guest OS
   to the templates are not terribly fast, and compilations can take
   20-30 seconds in some cases.


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

