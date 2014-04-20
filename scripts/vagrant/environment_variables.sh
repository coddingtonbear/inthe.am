if [ -z "$TRAVIS" ]; then
    # You *must* generate a pair of google oauth keys in order to
    # handle log-in correctly
    export TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=enter your key
    export TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=enter your secret

    # If you would like to be able to run integration tests, you'll need
    # to create a dummy google account, too
    export TWWEB_TESTING_LOGIN_USER=enter your testing account username
    export TWWEB_TESTING_LOGIN_PASSWORD=enter your testing account password
fi

# The below settings are unlikely to need to be changed for testing.
export TWWEB_TASKD_BINARY=/usr/local/bin/taskd
export TWWEB_TASKD_SERVER=127.0.0.1:53589
export TWWEB_TASKD_ORG=inthe_am
export TWWEB_TASK_BINARY=/usr/local/bin/task
export TWWEB_TASKD_DATA=/var/taskd
export TWWEB_TASKD_SIGNING_TEMPLATE=/var/taskd/cert.template
export DJANGO_SETTINGS_MODULE=inthe_am.settings
export PYTHONPATH=/var/www/twweb

# To more-accurately match production, set the following:
#export TWWEB_DATABASE_ENGINE=django.db.backends.postgresql_psycopg2
#export TWWEB_DATABASE_NAME=<your dbname>
#export TWWEB_DATABASE_USER=<your db user>
#export TWWEB_DATABASE_PASSWORD=<your db password>
#export TWWEB_DATABASE_HOST=<your db host>
