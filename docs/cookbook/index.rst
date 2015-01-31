Cookbook
========


To add items to this cookbook, click the 'Edit on Github'
button in the upper-right corner.

Making it easy to find tasks submitted via SMS
----------------------------------------------

If you're anything like me, you usually submit your tasks via SMS only
when you're on a crowded train or bumpy car ride, so your tasks are
abbreviated, often misspelled, and never include crucial information
like project information and due dates.

You can make it easy on yourself by setting Inthe.AM to automatically
add a high-coefficient tag to tasks incoming via SMS by making a minor
change to both your ``.taskrc`` file on Inthe.AM and your SMS configuration.

1. Update the field "Automatic Arguments" in "SMS Access" from your
   Configuration & Settings page to include the text ``+review``.
   This will cause all tasks incoming via SMS to have that tag added
   to its attributes.

2. Add a line to your ``.taskrc`` on Inthe.AM and locally that causes
   tasks having this tag to float to the top of your tasks list.
   
   For example::

       urgency.user.tag.review.coefficient=99

   The above urgency setting causes the urgency of tasks tagged with
   ``+review`` to increase by 99 points -- almost certainly higher
   than any other tasks you might have.

Now, once you're nearby your computer again, you'll find those tasks
at the top of your task list.

Making it easy to find tasks submitted via Email
------------------------------------------------

Every once in a while, a task that I need to accomplish comes to mind
when I'm far away from a computer and I might send my Inthe.AM account
a quick e-mail to add a task.  Usually, though, I don't specify enough
information, and want to add a little more data once it's in my task list.

You can easily add a tag to incoming tasks that makes those tasks
you've added appear at the top of your task list for easy prioritization
by following these short steps:

1. Add a contact to your e-mail contact list that automatically assigns a
   tag ``+review`` to the created task, so you can use it for finding tasks
   that you need to review and prioritize next time I'm nearby a computer.

   You can do this by adding ``+review`` to the end of your Inthe.AM
   e-mail address; for example, if your Inthe.AM e-mail address is
   ``9d2b26ef-c4cf-491b-8b9a-6a8d9fe67c72@inthe.am``, the e-mail
   address you'd add as a contact would be
   ``9d2b26ef-c4cf-491b-8b9a-6a8d9fe67c72+review@inthe.am``.

2. Add a line to your ``.taskrc`` on Inthe.AM and locally that causes
   tasks having this tag to float to the top of your tasks list.
   
   For example::

       urgency.user.tag.review.coefficient=99

   The above urgency setting causes the urgency of tasks tagged with
   ``+review`` to increase by 99 points -- almost certainly higher
   than any other tasks you might have.

Now, while you're on the go, you can just find that contact in your
contact list and send off a quick message.  When the task is added
to your task list, it'll appear at the top.
