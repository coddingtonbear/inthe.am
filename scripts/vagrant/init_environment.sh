# Install necessary packages
apt-get update
apt-get install -y git postgresql-server-dev-9.1 python-dev

# Set up virtual environment
mkdir -p /var/www/envs
if [ ! -d /var/www/envs/twweb ]; then
    wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    pip install virtualenv
    virtualenv /var/www/envs/twweb
    printf "\n\nsource /var/www/twweb/environment_variables.sh\n" >> /var/www/envs/twweb/bin/activate
fi
if [ ! -L /var/www/twweb/bin ]; then
    ln -s /var/www/envs/twweb/bin /var/www/twweb/bin
fi

# Install requirements
source /var/www/envs/twweb/bin/activate
pip install --download-cache=/tmp/pip_cache -r /var/www/twweb/requirements.txt
