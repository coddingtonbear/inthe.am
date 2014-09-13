Google OAuth Keys
=================

Follow the following steps to generate Google OAuth credentials to use for
development and testing.  These are used for the log-in process, and are
functionally essential for doing much of anything with Inthe.AM.

1. Go to `Google's developer console <https://console.developers.google.com/project>`_.
2. Create a new project.
3. From within your project, create a new "Client ID" by going to
   "APIs & Auth" > "Credentials" and clicking on the "Create New Client ID"
   button.
4. Select "Web Application"
5. Enter the following for 'Authorized Javascript Origins'::

    http://127.0.0.1
    http://localhost

6. Enter the following for 'Authorized Redirect URI'::

    http://127.0.0.1:8000/complete/google-oauth2/
    http://localhost:8081/complete/google-oauth2/

7. Save
8. You will be presented with your newly-generated client ID.
9. Enter the value of "Client ID" into your ``environment_variables.sh``
   as the value of the ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``.
10. Enter the value of "Client Secret" into your ``environment_variables.sh``
    as the value of the ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``.
11. If you are currently running an existing ``runserver`` session, you will
    want to close it, run ``source environment_variables.sh`` to update your
    environment with the environment variables you've set, and start the
    ``runserver`` once again.

