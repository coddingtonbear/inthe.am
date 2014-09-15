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
