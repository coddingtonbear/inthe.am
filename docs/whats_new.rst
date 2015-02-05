What's New?
===========

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
