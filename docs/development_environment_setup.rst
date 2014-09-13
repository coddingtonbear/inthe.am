
Setting up a Development Environment
====================================

1. Create the virtual machine ``vagrant up``
2. Enter the virtual machine: ``vagrant ssh``
3. Switch to the project directory: ``cd /var/www/twweb/``
4. Start the ``runserver`` by running ``python manage.py runserver 0.0.0.0:8000``

Troubleshooting your Development Environment
--------------------------------------------

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

  * Tests are ran against development (read: concatenated) assets rather
    than the assets that are 'uglified' for production.  Make sure that
    you have run ``grunt browserify concat`` before running tests.

