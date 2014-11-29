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
    sudo('/bin/chown -R www-data:www-data /var/www/twweb/logs/', shell=False)
    sudo('/usr/sbin/service twweb restart', shell=False)
    sudo('/usr/sbin/service twweb-status restart', shell=False)
    sudo('/usr/sbin/service twweb-celery restart', shell=False)
    local('git checkout development')
