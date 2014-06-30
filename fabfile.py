import os

from fabric.api import task, run, local, sudo, cd, env


env.hosts = [
    os.environ['TWWEB_HOST'],
]


def virtualenv(command, user=None):
    run('source /var/www/envs/twweb/bin/activate && ' + command)


@task
def deploy():
    local('git push origin development')
    local('git checkout master')
    local('git merge development')
    local('git push origin master')
    with cd('/var/www/twweb'):
        run('git fetch origin')
        run('git merge origin/master')
        run('npm install')
        run('grunt ember_handlebars sass browserify uglify')
        virtualenv('pip install -r /var/www/twweb/requirements.txt')
        virtualenv('python manage.py collectstatic --noinput')
        virtualenv('python manage.py migrate')
        sudo('service twweb restart')
        sudo('service twweb-status restart')
        sudo('service twweb-celery restart')
    local('git checkout development')
