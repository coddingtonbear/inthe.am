Setting up a Development Environment
====================================

Prerequisites
-------------

* `Vagrant <https://www.vagrantup.com/>`_
* `Virtualbox <https://www.virtualbox.org/>`_ or another Virtual Machine host supported by Vagrant
* The `vagrant-gatling-rsync <https://github.com/smerrill/vagrant-gatling-rsync>`_ plugin; you can install this by running::

    vagrant plugin install vagrant-gatling-rsync

Setup
-----

From a your clone of the Inthe.AM repository, run the following command to
bring up your development environment::

    vagrant up

That console window will now stop, showing "Watching: " until discovering
any filesystem changes.  For as long as that window is open, changes you
make to files in the repository will be automatically synchronized with
the development environment, and a message like "Rsyncing folder:" will
be displayed.

From another shell, go the folder where you've cloned the Inthe.AM repository
and run::

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

Then, you can start the server by running::

   python manage.py run

.. note::

   It will take about a 10 seconds for both of the underlying servers to start.
   Once you see the message "Build successful" in green, the server is ready.

Once the runserver is running, you'll be able to access your local copy of Inthe.AM
by going to `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_ in a browser.

Troubleshooting your Development Environment
--------------------------------------------

* Various environment variables are set in ``environment_variables.sh``,
  and you will need to set *at least* the following two environment variables
  to use the site; see :ref:`google_oauth_keys` for details regarding what you
  should set these variables to:

  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``

* "When trying to run ``python manage.py run``, I get a message reading
  'Error: That port is already in use.'".

  * While a browser window is open, one connection is persistently
    held open for streaming data from the server to the client as
    it has changed; this process will not close until it lost its
    connection with the browser.  Either close your browser tab
    showing that window or find the PID of the still-running process
    using ``ps -f``, and killing the running process with ``kill <that pid>``.
