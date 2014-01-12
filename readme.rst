**Nothing to see here!** At least, not yet.  This is very much in
WIP territory.

Problem
-------

* Adding/completing tasks with Taskwarrior can only be completed
  from a CLI.

Proposition 1
~~~~~~~~~~~~~

* Create a django-based web interface for managing tasks.
* Leverage DropBox integration for:

  * Using DropBox as the system of record for ones' tasks.

* Leverage Twilio integration for:

  * Allowing one to perform task-related commands via SMS.

Tasks
_____

- [X] Implement solution for finding ones task file(s) in a dropbox account.

  - [X] Dropbox OAuth Dance
  - [X] Using Access token, find all directories containing task files.
  - [X] Implement caching and storage managment:

    - [X] Only re-download if dropbox revision ID has changed.

  - [ ] Adding new tasks.
  - [X] Marking tasks as completed.

- [X] Implement UI (or borrow from `taskweb <https://github.com/campbellr/taskweb>`__).
- [ ] Implement Twilio integration
    - [ ] via SMS, run arbitrary ``tasks`` commands.

