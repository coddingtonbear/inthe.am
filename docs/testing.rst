Testing
=======

.. _running_tests:

Running Tests
-------------

You can easily run the tests from the development environment
by running the following command::

    python manage.py runtests

.. note::

   By default, tests run in PhantomJS, but if you would like to
   see the tests in action, you can run them in Firefox by adding the
   following line to the bottom of your ``settings.py`` file 
   (at ``inthe_am/settings.py``)::

        WEBDRIVER_BROWSER = 'firefox'

    and installing the requisite Ubuntu package by running the following
    command::

        sudo apt-get install firefox
