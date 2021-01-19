.. _development-environment-setup:

Setting up a Development Environment
====================================

Prerequisites
-------------

* `Docker <https://docker.com/>`_.

Setup
-----

Before starting your environment, you will need to generate a keypair for the HTTPS server. 
From a your clone of the Inthe.AM repository,
run the following commands::

    cd docker/nginx/secrets
    openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes

After that, you can bring up your development environment::

    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

.. note::

   Specifying the dockerfiles as shown above
   will launch your server in "development" mode.
   This has the following effects:

   - Your server is started using Django's built-in runserver.
     This runserver is configured to automatically restart
     should you make any changes to relevant source files.
   - A debugger is available on port 3000.
     This is pre-configured for use in Vscode
     via the "Connect to Django" debugger.
   - The event stream will be disabled; so you will need to manually
     refresh tasks using the "Refresh" button on the top of the screen.

   Running in this mode is useful for development,
   but does make it impossible for you to work on changes to the event stream.
   If you do need to make changes to the event stream,
   be sure to start the server in the more-basic way
   (i.e. ``docker-compose up``),
   but keep in mind that the other helpful functions provided to you
   will also no longer be available.

You can now access the site by connecting to `https://localhost/ <https://localhost/>`_.

Troubleshooting your Development Environment
--------------------------------------------

* Various environment variables are set in ``.private.env``,
  and you will need to set *at least* the following two environment variables
  to use the site; see :ref:`google_oauth_keys` for details regarding what you
  should set these variables to:

  * ``SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``
