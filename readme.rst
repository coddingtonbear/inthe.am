Inthe.AM
========

.. image:: https://travis-ci.org/coddingtonbear/inthe.am.png?branch=master
   :target: https://travis-ci.org/coddingtonbear/inthe.am

This is the source upon which http://inthe.am/ runs.

Feel free to post a pull request here to fix a bug or add a new feature.  I often hang out on freenode as @coddingtonbear.


Development
-----------

.. image:: https://travis-ci.org/coddingtonbear/inthe.am.png?branch=development
   :target: https://travis-ci.org/coddingtonbear/inthe.am

1. Create the virtual machine ``vagrant up``
2. Enter the virtual machine: ``vagrant ssh``
3. Switch to the project directory: ``cd /var/www/twweb/``
4. Enter the virtual environment: ``source bin/activate``
5. Start the ``runserver`` by running ``python manage.py runserver 0.0.0.0:8000``


Development Environment Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Various environment variables are set in ``environment_variables.sh``,
  and you will need to set *at least* need to set the following two to
  use the site; see `Google OAuth Keys`_:

  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``

* When trying to start ``runserver``, you get a message reading
  "Error: That port is already in use.".

  * While a browser window is open, one connection is persistently
    held open for streaming data from the server to the client as
    it has changed; this process will not close until it lost its
    connection with the browser.  Either close your browser tab
    showing that window or find the PID of the still-running process
    using ``ps -f``, and killing the running process with ``kill <that pid>``.

Google OAuth Keys
~~~~~~~~~~~~~~~~~

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

