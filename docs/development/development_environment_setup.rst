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

    docker-compose up

You can now access the site by connecting to `https://127.0.0.1/ <https://127.0.0.1/>`_.

Troubleshooting your Development Environment
--------------------------------------------

* Various environment variables are set in ``.private.env``,
  and you will need to set *at least* the following two environment variables
  to use the site; see :ref:`google_oauth_keys` for details regarding what you
  should set these variables to:

  * ``SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``
