Endpoints
=========

.. toctree::
   :maxdepth: 2

Pending Tasks
-------------

Task List
~~~~~~~~~

URL: ``https://inthe.am/api/v2/task/``

+----------+------------------------------------------+
| Method   | Description                              |
+==========+==========================================+
| ``GET``  | List all pending tasks.                  |
+----------+------------------------------------------+
| ``POST`` | Given a task payload, create a new task. |
+----------+------------------------------------------+

Task Details
~~~~~~~~~~~~

URL: ``https://inthe.am/api/v2/task/<TASK_UUID>/``

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

URL: ``https://inthe.am/api/v2/task/<TASK_UUID>/delete/``

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

URL: ``https://inthe.am/api/v2/task/<TASK_UUID>/start/``

+----------+-----------------------------------+
| Method   | Description                       |
+==========+===================================+
| ``POST`` | Mark an existing task as started. |
+----------+-----------------------------------+

Stop a Task 
~~~~~~~~~~~

URL: ``https://inthe.am/api/v2/task/<TASK_UUID>/stop/``

+----------+-----------------------------------+
| Method   | Description                       |
+==========+===================================+
| ``POST`` | Mark an existing task as stopped. |
+----------+-----------------------------------+


Feeds
-----

RSS Feed
~~~~~~~~

Returns an RSS representation of your current pending tasks.

.. note::

   This endpoint is not authenticated, and is thus disabled unless
   specifically enabled in your configuration.

   After enabling this endpoint in your configuration, you will be
   given the proper URL to use (including your ``SECRET_ID``).

URL: ``https://inthe.am/api/v2/task/feed/<SECRET_ID>/``

+---------+------------------------+
| Method  | Description            |
+=========+========================+
| ``GET`` | RSS Tasks Feed.        |
+---------+------------------------+


Utility Endpoints
-----------------

.. _repository_locking:

Repository Lock
~~~~~~~~~~~~~~~

.. warning::

   Do not use this endpoint unless you absolutely know what you are doing.
   Manually unlocking your repository while an action is in progress may
   result in data loss!

URL: ``https://inthe.am/api/v2/task/lock/``

+--------+------------------------------------------------------------+
| Method | Description                                                |
+========+============================================================+
| DELETE | Manually unlock your repository.                           |
+--------+------------------------------------------------------------+
| GET    | Check whether your repository is currently locked. Will    |
|        | return a 200 if it is, and a 404 if it is not.             |
+--------+------------------------------------------------------------+

Enable Synchronization
~~~~~~~~~~~~~~~~~~~~~~

You can re-enable synchronization if it has been disabled
by sending an empty ``POST`` to this endpoint.

URL: ``https://inthe.am/api/v2/user/enable-sync/``

+----------+--------------------------+
| Method   | Description              |
+==========+==========================+
| ``POST`` | Enable synchronization.  |
+----------+--------------------------+

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

URL: ``https://inthe.am/api/v2/user/status/``

+---------+----------------+
| Method  | Description    |
+=========+================+
| ``GET`` | Get user data. |
+---------+----------------+

Announcements
~~~~~~~~~~~~~

Returns a JSON-formatted list of recent announcements.

URL: ``https://inthe.am/api/v2/user/announcements/``

+---------+--------------------+
| Method  | Description        |
+=========+====================+
| ``GET`` | Get announcements. |
+---------+--------------------+

Download my certificate
~~~~~~~~~~~~~~~~~~~~~~~

Returns your currently-active certificate used for communicating with
Inthe.AM.

URL: ``https://inthe.am/api/v2/user/my-certificate/``

+---------+------------------+
| Method  | Description      |
+=========+==================+
| ``GET`` | Get certificate. |
+---------+------------------+

Download my key
~~~~~~~~~~~~~~~

Returns your currently-active key used for communicating with
Inthe.AM.

URL: ``https://inthe.am/api/v2/user/my-key/``

+---------+------------------+
| Method  | Description      |
+=========+==================+
| ``GET`` | Get key.         |
+---------+------------------+

Download CA certificate
~~~~~~~~~~~~~~~~~~~~~~~

Returns Inthe.AM's certificate; this is used for synchronizing with
Inthe.AM's taskd server.

URL: ``https://inthe.am/api/v2/user/ca-certificate/``

+---------+---------------------+
| Method  | Description         |
+=========+=====================+
| ``GET`` | Get CA certificate. |
+---------+---------------------+


Configuration
-------------

Update ``.taskrc``
~~~~~~~~~~~~~~~~~~

Locally, Inthe.AM runs Taskwarrior in a way that's very similar to
how you interact with Taskwarrior on your personal computer, and a
``.taskrc`` file is read and used for calculating things like UDAs
and priorities.

Use this endpoint to see or set your current ``.taskrc``'s contents on
Inthe.AM.

URL: ``https://inthe.am/api/v2/user/taskrc/``

+---------+----------------------------------+
| Method  | Description                      |
+=========+==================================+
| ``GET`` | Get ``.taskrc`` file's contents. |
+---------+----------------------------------+
| ``PUT`` | Set ``.taskrc`` file's contents. |
+---------+----------------------------------+

Generate a new taskserver certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like to regenerate your Taskserver certificate, usually
because your existing one has expired, you can do so using this endpoint.

URL: ``https://inthe.am/api/v2/user/generate-new-certificate/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Generate new Taskserver          |
|          | Certificate.                     |
+----------+----------------------------------+

Reset taskserver settings
~~~~~~~~~~~~~~~~~~~~~~~~~

If you've changed your Taskserver settings, but you'd like to reset
them such that Inthe.AM's built-in taskserver is utilized, send an empty
``POST`` request to this endpoint.

.. note::

   Using this endpoint does a number of things:

   1. Resets your Taskserver synchronization settings such that Inthe.AM
      will synchronize with the built-in Taskserver.
   2. Clears any previously-synced tasks from your Inthe.AM Taskserver
      account.  This is to make sure that you have a clean slate.
   3. Clears the local Taskwarrior repository's ``backlog.data`` file.

   None of these should be considered particularly dangerous, but this
   is **not** an operation that can be undone without administrative
   intervention.

URL: ``https://inthe.am/api/v2/user/reset-taskd-configuration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Reset Taskserver configuration.  |
+----------+----------------------------------+

SMS messaging (Twilio) integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure or enable SMS integration by
sending a ``POST`` request to this endpoint with
two form-encoded variables:

* ``twilio_auth_token``: Your Twilio Auth Token.  This is used for
  authenticating the SMS request from Twilio.
* ``sms_whitelist``: A newline-separated list of phone numbers from
  which you would like to accept new tasks.
* ``sms_replies``: An integer indicating under what conditions should
  Inthe.AM send SMS message replies.  See the table below for information
  about what values are appropriate:

  +-------+--------------------------------------------+
  | Value | Meaning                                    |
  +=======+============================================+
  | 0     | Do not reply to any incoming text messages |
  +-------+--------------------------------------------+
  | 5     | Reply only to error messages               |
  +-------+--------------------------------------------+
  | 9     | Reply to all messages                      |
  +-------+--------------------------------------------+

URL: ``https://inthe.am/api/v2/user/twilio-integration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Configure SMS Integration.       |
+----------+----------------------------------+

Email integration
~~~~~~~~~~~~~~~~~

You can configure which e-mail addresses are allowed to send new
tasks to your personal task creation e-mail address by sending a ``POST``
to this address with the following form-encoded variable:

* ``email_whitelist``: A newline-separated list of e-mail addresses from
  which you will allow new tasks to be created when an e-mail email message
  is received.

URL: ``https://inthe.am/api/v2/user/email-integration/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Configure Email Integration.     |
+----------+----------------------------------+

Clear task data
~~~~~~~~~~~~~~~

You can clear your taskserver information by sending a ``POST`` request
to this endpoint.

Please note that this does not permanently delete your task information;
it only clears your taskserver information; if you would like your
taskserver information cleared permanently, please send an email to
admin@inthe.am.

URL: ``https://inthe.am/api/v2/user/clear-task-data/``

+----------+----------------------------------+
| Method   | Description                      |
+==========+==================================+
| ``POST`` | Clear Taskserver information.    |
+----------+----------------------------------+

Colorscheme
~~~~~~~~~~~

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

URL: ``https://inthe.am/api/v2/user/colorscheme/``

+---------+--------------------------+
| Method  | Description              |
+=========+==========================+
| ``GET`` | Get current colorscheme. |
+---------+--------------------------+
| ``PUT`` | Set colorscheme.         |
+---------+--------------------------+


RSS feeds
~~~~~~~~~

You can enable or disable the RSS feed showing your upcoming tasks by
sending a ``POST`` request:

* To enable: Send a single form-encoded parameter -- ``enabled`` in the
  request.
* To disable: Send an empty request.

URL: ``https://inthe.am/api/v2/user/feed-config/``

+----------+--------------------------+
| Method   | Description              |
+==========+==========================+
| ``POST`` | Enable/Disable RSS feed. |
+----------+--------------------------+

