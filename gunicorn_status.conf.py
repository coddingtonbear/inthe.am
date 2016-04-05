#from gevent.monkey import patch_all
#patch_all()

user = 'www-data'
group = 'www-data'
logfile = '/var/www/twweb/logs/gunicorn-status.log'
workers = 3
loglevel = 'info'
bind = '127.0.0.1:8041'
timeout = 300
worker_connections = 1000
name = 'inthe_am_status'
preload = True
worker_class = 'eventlet'
