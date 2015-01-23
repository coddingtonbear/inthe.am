Cookbook
========


Quickly adding tasks to your task list while on-the-go
------------------------------------------------------

Every once in a while, a task that I need to accomplish comes to mind
when I'm far away from a computer; I add quick tasks to my task list by:

1. Adding a contact to my e-mail inbox that automatically assigns a
   tag ``+review`` to the created task that I can use for finding tasks
   that I need to review and prioritize next time I'm nearby a computer.

   You can do this by adding ``+review`` to the end of your Inthe.AM
   e-mail address; for example, if your Inthe.AM e-mail address is
   ``9d2b26ef-c4cf-491b-8b9a-6a8d9fe67c72@inthe.am``, the e-mail
   address you'd add as a contact would be
   ``9d2b26ef-c4cf-491b-8b9a-6a8d9fe67c72+review@inthe.am``.

2. Adding a line to my ``.taskrc`` file that causes those tasks to float
   to the top of my task list.

   For example::

       urgency.user.tag.review.coefficient=99


Now, while you're on the go, you can just find that contact in your
contact list and send off a quick message.  When the task is added
to your task list, it'll appear at the top.
