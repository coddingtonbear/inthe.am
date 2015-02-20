What's New?
===========

19 February 2015
----------------

Features
~~~~~~~~

* Added functionality allowing a user to configure under what circumstances
  should Inthe.AM reply to incoming text messages;
  `this addresses concerns raised in  #164 <https://github.com/coddingtonbear/inthe.am/issues/174>`_.

16 February 2015
----------------

Features
~~~~~~~~

* (Private Beta) Team Kanban Boards: Added configurable Kanban Board
  functionality allowing teams to collaborate on shared tasks.
  Completes Phase 1 of `#146 Kanban Board <https://github.com/coddingtonbear/inthe.am/issues/146>`_.

Technical
~~~~~~~~~

* Updated sync behavior in a few fundamental ways:

  * Inthe.AM will automatically synchronize local user task lists as sync
    events are seen in the Taskserver logs.
  * Rather than periodically initiating a sync while connected to the
    status stream; simply waits for head changes from the synchronization
    operation finished in the above step.
  * Users using non-local Taskservers will no longer have access to streaming
    task information, and will instead need to click the 'Refresh' button
    to synchronize tasks.

* Removed functionality allowing one to disable the task update stream.  Very
  few users were using the functionality allowing one to disable it.

Deprecation Warnings
~~~~~~~~~~~~~~~~~~~~

* Synchronization using non-local Taskservers will be disabled after
  1 April 2015.  Configuring an existing account to synchronize
  with a non-local Taskserver will be disabled in the near future.
  See `#167: Deprecate synchronization using non-local Taskservers <https://github.com/coddingtonbear/inthe.am/issues/167>`_ for more information.

30 January 2015
---------------

Features
~~~~~~~~

* Attachment annotations: New attachments will now add annotations containing
  a link to the uploaded attachment in S3; this makes it easier to access your
  annotations when using Taskwarrior clients other than Inthe.AM.
* Automatic SMS arguments: You can now specify default tags and attributes for
  incoming SMS messages; this makes it easy for you to make sure you can those
  messages you wrote while on a bumpy bus or train so you can clean up those
  tasks later.

18 January 2015
---------------

Features
~~~~~~~~

* Updated `documentation <http://intheam.readthedocs.org/en/latest/index.html>`_ and added link to documentation to the page UI.

Technical
~~~~~~~~~

* Updated front-end Javascript code to use `Ember-CLI <http://www.ember-cli.com/>`_ to remove the
  existing one-off Javascript bundle build process.
* Completed `#133: "Switch from using one-off $.ajax requests to using promises." <https://github.com/coddingtonbear/inthe.am/issues/133>`_.
* Completed `#132: "Show loading animation when perfoming XHRs from the configuration page." <https://github.com/coddingtonbear/inthe.am/issues/132>`_.
* Completed `#131: "Display returned errors rather than a generic error message when interacting with the configuration page." <https://github.com/coddingtonbear/inthe.am/issues/131>`_.

Bugfixes
~~~~~~~~

* Fixed `#141: "Single-byte characters in task content may cause UnicodeDecodeError to be raised." <https://github.com/coddingtonbear/inthe.am/issues/141>`_.

1 January 2015
--------------

Bugfixes
~~~~~~~~

* Fixed `#134: "Emailing tasks does not work if you use an alias" <https://github.com/coddingtonbear/inthe.am/issues/134>`_.

15 December 2014
----------------

Features
~~~~~~~~

* Added keyboard shortcuts and the ``?`` UI.
* Created `Taskwarrior Inthe.AM Utility <https://github.com/coddingtonbear/taskwarrior-inthe.am>`_.
