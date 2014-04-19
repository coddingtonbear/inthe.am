Inthe.AM
========

This is the source upon which http://inthe.am/ runs.

Feel free to post a pull request here to fix a bug or add a new feature.  I often hang out on freenode as @coddingtonbear.


Development
-----------

1. ``vagrant up``
2. ``vagrant ssh``
3. ``cd /var/www/twweb/``
4. ``python manage.py runserver 0.0.0.0:8000``


Development Environment Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Various environment variables are set in ``environment_variables.sh``,
  and you will need to set *at least* need to set the following two to
  use the site:

  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``
  * ``TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``

