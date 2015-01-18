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
   see the tests in action, you can run them in Firefox by setting
   the the ``TWWEB_WEBDRIVER_BROWSER`` environment variable to
   ``firefox``; for example::

        TWWEB_WEBDRIVER_BROWSER=firefox python manage.py runtests

