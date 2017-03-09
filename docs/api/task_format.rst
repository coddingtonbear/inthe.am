Task Format
===========

Each task has at least the following fields:

+------------------+-------------------------------------------------------------------------+
| Field            | Description                                                             |
+==================+=========================================================================+
| ``id``           | (**read-only**, **primary key**) The unique ID number of a task. These  |
|                  | are stable and can be used in situations where you may want to retrieve |
|                  | a task after it has been completed.                                     |
+------------------+-------------------------------------------------------------------------+
| ``uuid``         | (**read-only**, **primary key**) **DEPRECATED** Please use ``id`` to    |
|                  | fetch your task's ID number.                                            |
+------------------+-------------------------------------------------------------------------+
| ``short_id``     | (**read-only**, **primary key**) Returns the short ID of the task.      |
|                  | Note that this number is **unstable** and will change as tasks are      |
|                  | added/removed from the pending task list.                               |
+------------------+-------------------------------------------------------------------------+
| ``resource_uri`` | (**read-only**) This is the URL at which this task can be retrieved     |
|                  | again in the future. It will match the URL you used for fetching this   |
|                  | task unless you fetched this task from a listing endpoint.              |
+------------------+-------------------------------------------------------------------------+
| ``status``       | One of 'pending', 'completed', 'waiting', or 'deleted'. New tasks       |
|                  | default to 'pending'.                                                   |
+------------------+-------------------------------------------------------------------------+
| ``urgency``      | (**read-only**) A float representing the current calculated urgency     |
|                  | level of a task. This is generated internally by Taskwarrior.           |
+------------------+-------------------------------------------------------------------------+
| ``description``  | The title of the task.                                                  |
+------------------+-------------------------------------------------------------------------+
| ``priority``     | One of 'H', 'M', or 'L'.                                                |
+------------------+-------------------------------------------------------------------------+
| ``due``          | A date string [#datestring]_ representing this task's due date and      |
|                  | time.                                                                   |
+------------------+-------------------------------------------------------------------------+
| ``entry``        | (**read-only**) A date string [#datestring]_ representing this task's   |
|                  | entry date and time.                                                    |
+------------------+-------------------------------------------------------------------------+
| ``modified``     | (**read-only**) A date string [#datestring]_ representing the last time |
|                  | that this task was modified.                                            |
+------------------+-------------------------------------------------------------------------+
| ``start``        | A date string [#datestring]_ representing the date and time this task   |
|                  | was last started.                                                       |
+------------------+-------------------------------------------------------------------------+
| ``wait``         | A date string [#datestring]_ representing the minimum date and time at  |
|                  | which this task should appear in the pending task list.                 |
+------------------+-------------------------------------------------------------------------+
| ``scheduled``    | A date string [#datestring]_ representing the minimum date and time at  |
|                  | which this task is scheduled.                                           |
+------------------+-------------------------------------------------------------------------+
| ``depends``      | A list of tasks upon which this task is dependent.                      |
+------------------+-------------------------------------------------------------------------+
| ``annotations``  | A list of annotations added to the task [#annotations]_.                |
+------------------+-------------------------------------------------------------------------+
| ``tags``         | A list of tags assigned to this task.                                   |
+------------------+-------------------------------------------------------------------------+
| ``imask``        | (**read-only**) A value representing this task's ``imask``. This is a   |
|                  | property used internally by Taskwarrior for recurring tasks.            |
+------------------+-------------------------------------------------------------------------+

The task is formatted into JSON for use by the API; for example, below is a JSON-formatted
task:

.. code-block:: json

    {
        "annotations": [
            "Chapter 1",
            "Chapter 2",
        ],
        "depends": null,
        "description": "The wheels on the bus go round and round",
        "due": null,
        "entry": "2014-02-03T01:52:51Z",
        "id": 1,
        "imask": null,
        "modified": "2014-02-03T01:52:51Z",
        "priority": null,
        "project": "Alphaville",
        "scheduled": null,
        "start": null,
        "status": "waiting",
        "tags": ["very_unimportant", "delayed"],
        "urgency": -0.1,
        "uuid": "b8d05cfe-8464-44ef-9d99-eb3e7809d337",
        "wait": "Thu, 6 Feb 2014 01:52:51 +0000"
    }

.. warning::

   If you neglect to supply a timezone offset in a supplied date string, the incoming date string will be
   interpreted to be a UTC timestamp.

.. [#datestring] ISO-8601 format.
