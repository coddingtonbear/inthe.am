source scripts/vagrant/environment_variables.sh
source $HOME/.nvm/nvm.sh
export PATH=/var/www/twwweb/node_modules/.bin:$PATH
nvm use 5
python manage.py runtests --failfast
