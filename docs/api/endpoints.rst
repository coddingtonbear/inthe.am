Endpoints
=========

Common Response Codes
---------------------

All endpoints share the following list of common response codes unless otherwise elaborated
upon below.

+---------------+-------------------------------------------------------------------------------+
| Response Code | Description                                                                   |
+===============+===============================================================================+
| 200           | Success                                                                       |
+---------------+-------------------------------------------------------------------------------+
| 201           | Successfully created                                                          |
+---------------+-------------------------------------------------------------------------------+
| 400           | Your request was malformed, or the requested operation was impossible. A      |
|               | description of the problem will be included in the response.                  |
+---------------+-------------------------------------------------------------------------------+
| 401           | Your request did not include proper authentication headers. Make sure that    |
|               | you have properly sent the Authorization header described in                  |
|               | :ref:`authentication`.                                                        |
+---------------+-------------------------------------------------------------------------------+
| 403           | Your request was not properly authenticated or you have requested an entity   |
|               | for which you do not have access. Make sure that you have properly sent the   |
|               | Authorization header described in :ref:`authentication`.                      |
+---------------+-------------------------------------------------------------------------------+
| 404           | The entity you requested does not exist.                                      |
+---------------+-------------------------------------------------------------------------------+
| 405           | The request method used is not allowed for the endpoint you are sending it    |
|               | to. Please review the below documentation and alter your request to use an    |
|               | acceptable method.                                                            |
+---------------+-------------------------------------------------------------------------------+
| 409           | Your repository is currently locked. See :ref:`repository_locking` for more   |
|               | details.                                                                      |
+---------------+-------------------------------------------------------------------------------+
| 500           | A server error occurred while processing your request. An error was logged    |
|               | and the administrators of the site have been notified. Please try your        |
|               | request again later.                                                          |
+---------------+-------------------------------------------------------------------------------+

Pending Tasks
-------------

Task List
~~~~~~~~~

URL: ``https://inthe.am/api/v1/task/``

+----------+------------------------------------------+
| Method   | Description                              |
+==========+==========================================+
| ``GET``  | List all pending tasks.                  |
+----------+------------------------------------------+
| ``POST`` | Given a task payload, create a new task. |
+----------+------------------------------------------+

Task Details
~~~~~~~~~~~~

URL: ``https://inthe.am/api/v1/task/<TASK_UUID>/``

+------------+-------------------------------------------------------+
| Method     | Description                                           |
+============+=======================================================+
| ``GET``    | Get task details.                                     |
+------------+-------------------------------------------------------+
| ``PUT``    | Given a JSON task payload, update the task's details. |
+------------+-------------------------------------------------------+
| ``DELETE`` | Mark the existing task as completed.                  |
+------------+-------------------------------------------------------+

Non-users of Taskwarrior may be surprised by the ``DELETE`` method's
behavior of this endpoint given that the task is not actually deleted, but
instead marked as completed, but this implementation is much more consistent
with Taskwarrior workflows.


.. note::

   To truly delete a task, see :ref:`deleting-a-task` below.

.. _deleting-a-task:

Delete a Task 
~~~~~~~~~~~~~

URL: ``https://inthe.am/api/v1/task/<TASK_UUID>/delete/``

+----------+-----------------------------------+
| Method   | Description                       |
+==========+===================================+
| ``POST`` | Mark an existing task as deleted. |
+----------+-----------------------------------+

Although using the ``DELETE`` method on the
Task Details endpoint may seem to be more intuitive, it is far
more common for one to mark a task as completed than deleted.

If that doesn't set your mind at ease, try to think
of the Task List and Task Details endpoints as being listings of
only pending tasks, and that by issuing a ``DELETE`` request
you're removing it from your pending task list (and 
moving it to your completed task list).

Start a Task 
~~~~~~~~~~~~

URL: ``https://inthe.am/api/v1/task/<TASK_UUID>/start/``

+----------+-----------------------------------+
| Method   | Description                       |
+==========+===================================+
| ``POST`` | Mark an existing task as started. |
+----------+-----------------------------------+

Stop a Task 
~~~~~~~~~~~

URL: ``https://inthe.am/api/v1/task/<TASK_UUID>/start/``

+----------+-----------------------------------+
| Method   | Description                       |
+==========+===================================+
| ``POST`` | Mark an existing task as stopped. |
+----------+-----------------------------------+

Completed Tasks
---------------

Task List
~~~~~~~~~

URL: ``https://inthe.am/api/v1/completedtask/``

+---------+---------------------------+
| Method  | Description               |
+=========+===========================+
| ``GET`` | List all completed tasks. |
+---------+---------------------------+

Task Details
~~~~~~~~~~~~

URL: ``https://inthe.am/api/v1/completedtask/<TASK_UUID>/``

+---------+-----------------------------+
| Method  | Description                 |
+=========+=============================+
| ``GET`` | Get completed task details. |
+---------+-----------------------------+

Utility Endpoints
-----------------

Pebble Cards
~~~~~~~~~~~~

Returns a JSON representation of your current highest-priority task
for use by `Pebble Cards <https://keanulee.com/pebblecards/>`_.

.. note::

   This endpoint is not authenticated, and is thus disabled unless
   specifically enabled in your configuration.

URL: ``https://inthe.am/api/v1/task/pebble-card/<SECRET_ID>/``

+---------+------------------------+
| Method  | Description            |
+=========+========================+
| ``GET`` | Get Pebble Cards data. |
+---------+------------------------+

User Information
----------------

Status
~~~~~~

Returns brief JSON-formatted information about the currently
logged-in user.

.. note::

   This endpoint does not require authentication.  If you are not
   authenticated via an API key or a cookie, you will receive only
   limited information.

URL: ``https://inthe.am/api/v1/user/status/``

+---------+----------------+
| Method  | Description    |
+=========+================+
| ``GET`` | Get user data. |
+---------+----------------+

Announcements
~~~~~~~~~~~~~

Returns a JSON-formatted list of recent announcements.

URL: ``https://inthe.am/api/v1/user/announcements/``

+---------+--------------------+
| Method  | Description        |
+=========+====================+
| ``GET`` | Get announcements. |
+---------+--------------------+

Download My Certificate
~~~~~~~~~~~~~~~~~~~~~~~

Returns your currently-active certificate used for communicating with
Inthe.AM.

URL: ``https://inthe.am/api/v1/user/my-certificate/``

+---------+------------------+
| Method  | Description      |
+=========+==================+
| ``GET`` | Get certificate. |
+---------+------------------+

Download My Key
~~~~~~~~~~~~~~~

Returns your currently-active key used for communicating with
Inthe.AM.

URL: ``https://inthe.am/api/v1/user/my-key/``

+---------+------------------+
| Method  | Description      |
+=========+==================+
| ``GET`` | Get key.         |
+---------+------------------+

Download CA Certificate
~~~~~~~~~~~~~~~~~~~~~~~

Returns Inthe.AM's certificate; this is used for synchronizing with
Inthe.AM's taskd server.

URL: ``https://inthe.am/api/v1/user/ca-certificate/``

+---------+---------------------+
| Method  | Description         |
+=========+=====================+
| ``GET`` | Get CA certificate. |
+---------+---------------------+

Set or Get ``.taskrc`` Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Locally, Inthe.AM runs Taskwarrior in a way that's very similar to
how you interact with Taskwarrior on your personal computer, and a
``.taskrc`` file is read and used for calculating things like UDAs
and priorities.

Use this endpoint to see or set your current ``.taskrc``'s contents on
Inthe.AM.

URL: ``https://inthe.am/api/v1/user/taskrc/``

+---------+----------------------------------+
| Method  | Description                      |
+=========+==================================+
| ``GET`` | Get ``.taskrc`` file's contents. |
+---------+----------------------------------+
| ``PUT`` | Set ``.taskrc`` file's contents. |
+---------+----------------------------------+

Reset Taskserver Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you've changed your Taskserver settings, but you'd like to reset
them such that Inthe.AM's built-in taskserver is utilized, send an empty
``POST`` request to this endpoint.

URL: ``https://inthe.am/api/v1/user/reset-taskd-configuration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Reset Taskserver configuration.  |
+----------+----------------------------------+

SMS Messaging (Twilio) Integration Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure or enable SMS integration by
sending a ``POST`` request to this endpoint with
two form-encoded variables:

* ``twilio_auth_token``: Your Twilio Auth Token.  This is used for
  authenticating the SMS request from Twilio.
* ``sms_whitelist``: A newline-separated list of phone numbers from
  which you would like to accept new tasks.

URL: ``https://inthe.am/api/v1/user/twilio-integration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Configure SMS Integration.       |
+----------+----------------------------------+

Email Integration Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure which e-mail addresses are allowed to send new
tasks to your personal task creation e-mail address by sending a ``POST``
to this address with the following form-encoded variable:

* ``email_whitelist``: A newline-separated list of e-mail addresses from
  which you will allow new tasks to be created when an e-mail email message
  is received.

URL: ``https://inthe.am/api/v1/user/email-integration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Configure Email Integration.     |
+----------+----------------------------------+

Clear Task Data
~~~~~~~~~~~~~~~

You can clear your taskserver information by sending a ``POST`` request
to this endpoint.

Please note that this does not permanently delete your task information;
it only clears your taskserver information; if you would like your
taskserver information cleared permanently, please send an email to
admin@inthe.am.

URL: ``https://inthe.am/api/v1/user/clear-task-data/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Clear Taskserver information.    |
+----------+----------------------------------+

Colorscheme Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure the colorscheme used when displaying your tasks
by sending a ``PUT`` request to this URL having a body matching
the colorscheme you would like to use.

Options include:

* ``light-16.theme``
* ``dark-16.theme``
* ``light-256.theme``
* ``dark-256.theme``
* ``dark-red-256.theme``
* ``dark-green-256.theme``
* ``dark-blue-256.theme``
* ``dark-violets-256.theme``
* ``dark-yellow-green.theme`` (default)
* ``dark-gray-256.theme``
* ``solarized-dark-256.theme``
* ``solarized-light-256.theme``

You can also send a ``GET`` request to find the name of the colorscheme
currently in use.

URL: ``https://inthe.am/api/v1/user/colorscheme/``

+---------+--------------------------+
| Method  | Description              |
+=========+==========================+
| ``GET`` | Get current colorscheme. |
+---------+--------------------------+
| ``PUT`` | Set colorscheme.         |
+---------+--------------------------+
