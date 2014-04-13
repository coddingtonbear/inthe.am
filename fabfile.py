from fabric.api import task, run, local, sudo, cd, env


env.hosts = [
    'acodding@eugene.adamcoddington.net:22424',
]


def virtualenv(command, user=None):
    if user:
        sudo(
            'source /var/www/envs/twweb/bin/activate && ' + command,
            user=user
        )
    else:
        run('source /var/www/envs/twweb/bin/activate && ' + command)


@task
def deploy():
    local('git push origin master')
    with cd('/var/www/twweb'):
        run('git pull')
        run('grunt ember_handlebars sass browserify')
        virtualenv('pip install -r /var/www/twweb/requirements.txt')
        virtualenv('python manage.py collectstatic --noinput', user='www-data')
        virtualenv('python manage.py migrate', user='www-data')
        sudo('service twweb restart')
        sudo('service twweb-status restart')
        sudo('service twweb-celery restart')
