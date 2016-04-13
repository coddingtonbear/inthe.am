import copy
import json
import os

from fabric.api import task, run, local, sudo, cd, env
from fabric.context_managers import settings


env.hosts = [
    os.environ['TWWEB_HOST'],
]


def virtualenv(command, user=None):
    run('source /var/www/envs/twweb/bin/activate && ' + command)


@task
def deploy(
    install='yes', build='yes', chown='no', refresh='yes', announce='yes'
):
    pubsub_message = {
        'data': {
            'should_refresh': True if refresh == 'yes' else False
        },
        'system': True,
    }
    pre_message = copy.copy(pubsub_message)
    pre_message['type'] = 'deploy_started'
    post_message = copy.copy(pubsub_message)
    post_message['type'] = 'deploy_finished'

    local('git push origin development')
    local('git checkout master')
    local('git merge development')
    local('git push origin master')
    local('git checkout development')

    run(
        "redis-cli -n 1 PUBLISH __general__ '%s'" % json.dumps(pre_message)
    )
    if chown == 'yes':
        sudo('/bin/chown -R www-data:www-data /var/www/twweb', shell=False)
    if build == 'yes':
        # Restart celery in case it's using a lot of memory -- which is
        # totally a possibility.
        sudo('/usr/sbin/service twweb-celery restart', shell=False)
    with cd('/var/www/twweb'):
        run('git fetch origin')
        run('git merge origin/master')
        if install == 'yes':
            run('bower install')
            run('npm install')
            virtualenv('pip install -r /var/www/twweb/requirements-frozen.txt')
        if build == 'yes':
            # Clear out vendor sourcemaps
            with settings(warn_only=True):
                run(
                    "grep -lr --include=*.js sourceMappingURL "
                    "bower_components/ | xargs sed -i 's/sourceMappingURL//g'"
                )
            run('ember build --environment=production')
        virtualenv('python manage.py collectstatic --noinput')
        virtualenv('python manage.py migrate')
    sudo('/bin/chown -R www-data:www-data /var/www/twweb/logs/', shell=False)
    run(
        "redis-cli -n 1 PUBLISH __general__ '%s'" % json.dumps(post_message)
    )
    sudo('/usr/sbin/service twweb restart', shell=False)
    sudo('/usr/sbin/service twweb-status restart', shell=False)
    sudo('/usr/sbin/service twweb-celery restart', shell=False)
    sudo('/usr/sbin/service twweb-sync-listener restart', shell=False)
    sudo('/usr/sbin/service twweb-log-consumer restart', shell=False)
    sudo('/bin/chown -R www-data:www-data /var/www/twweb/logs/', shell=False)

    if announce == 'yes':
        commit = local('git rev-parse HEAD', capture=True)
        virtualenv(
            "curl --data-urlencode \"message=[Deploy completed successfully.]"
            "(https://github.com/coddingtonbear/inthe.am/commit/%s)\" "
            "$GITTER_WEBHOOK_URL" % (
                commit,
            )
        )
