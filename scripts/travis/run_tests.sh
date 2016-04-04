source scripts/vagrant/environment_variables.sh
source $HOME/.nvm/nvm.sh
nvm use 5
python manage.py runtests --failfast
