Setting up a Development Environment
====================================

Prerequisites
-------------

* `Vagrant <https://www.vagrantup.com/>`_
* `Virtualbox <https://www.virtualbox.org/>`_ or another Virtual Machine host supported by Vagrant

Setup
-----

From a your clone of the Inthe.AM repository, run the following commands::

    vagrant up
    vagrant ssh

After running ``vagrant ssh``, you're automatically SSH'd into your virtual machine,
and can start the development environment by first switching to the directory
holding your clone of the Inthe.AM repository::

    cd /var/www/twweb

.. note::

   You'll note that the path above -- ``/var/www/twweb`` -- probably doesn't
   match the path to where you've cloned the Inthe.AM repository, but are 
   in fact the same files.  Virtualbox provides a mechanism for mapping directories
   between the host OS (your computer) and the guest OS (the development environment)
   magically for you.

Then, you can start the runserver by running::

   python manage.py runserver 0.0.0.0:8000

Once the runserver is running, you'll be able to access your local copy of Inthe.AM
by going to `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_ in a browser.

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

