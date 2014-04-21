source scripts/vagrant/environment_variables.sh
celery -A inthe_am.taskmanager multi start worker1
python manage.py test taskmanager
