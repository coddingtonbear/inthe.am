# You *must* generate a pair of google oauth keys in order to
# handle log-in correctly
export TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=enter your key
export TWWEB_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=enter your secret
export TWWEB_TASKD_BINARY=/usr/local/bin/taskd
export TWWEB_TASKD_SERVER=127.0.0.1:53589
export TWWEB_TASKD_ORG=inthe_am
export TWWEB_TASK_BINARY=/usr/local/bin/task
export TWWEB_TASKD_DATA=/var/taskd
export TWWEB_TASKD_SIGNING_TEMPLATE=/var/taskd/cert.template
# To more-accurately match production, set the following:
#export TWWEB_DATABASE_ENGINE=django.db.backends.postgresql_psycopg2
#export TWWEB_DATABASE_NAME=<your dbname>
#export TWWEB_DATABASE_USER=<your db user>
#export TWWEB_DATABASE_PASSWORD=<your db password>
#export TWWEB_DATABASE_HOST=<your db host>
