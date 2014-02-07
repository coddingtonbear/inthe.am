user = 'www-data'
group = 'www-data'
logfile = '/var/www/twweb/logs/gunicorn.log'
workers = 20
loglevel = 'debug'
bind = '127.0.0.1:8040'
timeout = 300
