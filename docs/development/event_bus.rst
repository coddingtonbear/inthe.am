Event Bus Messages
==================

Inthe.AM relies on a Redis PubSub queue for interprocess communication;
these events convey real-time information
about things like when a synchronization has taken place,
and what tasks were changed.
Below, organized by emitting service, you'll find information about
what sorts of information can be found on the event bus.


Web
---

`__general__`
~~~~~~~~~~~~~

Emitted to send out general public announcements.

.. code-block:: ts

   interface Message {
      title: string  // Toast message title
      message: string  // Toast message body
      system: boolean
   }

`personal.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~

Emitted to cause a toast message to be displayed
to a particular user.

.. code-block:: ts

   interface Message {
     username: string
     title: string  // Toast message title
     message: string  // Toast message body
   }

`local_sync.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~~~

Emitted after a synchronous synchronization
between the Inthe.AM web interface
and the Taskd server has completed.

.. code-block:: ts

   interface Message {
     username: string
     debounce_id: string  // Used for debouncing sync requests
     start: str  // Git SHA
     head: str  // Git SHA
   }

`changed_task.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~~~~~

After completing any task operation,
one message of this type is emitted for every changed task.

.. code-block:: ts

   interface Message {
     username: string
     start: string  // Git SHA
     head: string  // Git SHA
     task_id: string  // UUID
     task_data: {
       [key: string]: any
     }
     changes: {
       [key: string]: str[]
     }
   }

`log_message.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~~~~

Emitted when a new log message is written
to a user's taskstore logs.

.. code-block:: ts

   interface Message {
     username: string
     md5hash: string // Deduplication hash
     last_seen: string  // Datetime
     created: string  // Datetime
     error: boolean
     silent: boolean
     message: string
     count: number  // Number of times this message has been seen
   }

`incoming_mail.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ts

   interface Message {
     username: string
     message_id: number
     subject: string
     accepted: boolean
     rejection_reason?: 'passlist' | 'subject'  // If not accepted
     task_id?: string  // UUID
   }


Taskd
-----

`sync.<USERNAME>`
~~~~~~~~~~~~~~~~~

Emitted immediately after completion of a sync event.

.. code-block:: ts

   interface Message {
      action: 'sync'
      username: string
      org: string
      client: string
      ip: string
      port: number
      client_key: string
      record_count: number
      branch_point: string
      branch_record_count: number
      delta_count: number
      stored_count: number
      merged_count: number
      service_duration: number
   }

`taskd.certificate.<USERNAME>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Emitted at the conclusion of determining
whether a user-provided synchronization certificate
should be accepted.

.. code-block:: ts

   interface Message {
      username: string
      org: string
      client: string
      ip: string
      port: number
      fingerprint: string
      certificate_recognized: bool
      certificate_accepted: bool
   }
