import os

from fabric.api import task, run, local, sudo, cd, env


env.hosts = [
    os.environ['TWWEB_HOST'],
]


def virtualenv(command, user=None):
    run('source /var/www/envs/twweb/bin/activate && ' + command)


@task
def deploy(install='yes', build='yes', chown='no'):
    local('git push origin development')
    local('git checkout master')
    local('git merge development')
    local('git push origin master')
    with cd('/var/www/twweb'):
        if chown == 'yes':
            sudo('chown -R www-data:www-data .')
        run('git fetch origin')
        run('git merge origin/master')
        if install == 'yes':
            run('bower install')
            run('npm install')
            virtualenv('pip install -r /var/www/twweb/requirements-frozen.txt')
        if build == 'yes':
            run('ember build --environment=production')
        virtualenv('python manage.py collectstatic --noinput')
        virtualenv('python manage.py migrate')
    sudo('/bin/chown -R www-data:www-data /var/www/twweb/logs/', shell=False)
    sudo('/usr/sbin/service twweb restart', shell=False)
    sudo('/usr/sbin/service twweb-status restart', shell=False)
    sudo('/usr/sbin/service twweb-celery restart', shell=False)
    sudo('/usr/sbin/service twweb-sync-listener restart', shell=False)
    sudo('/usr/sbin/service twweb-log-consumer restart', shell=False)
    sudo('/bin/chown -R www-data:www-data /var/www/twweb/logs/', shell=False)
    local('git checkout development')
