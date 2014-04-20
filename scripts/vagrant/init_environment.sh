STARTING_DIR=$(pwd)

# Install necessary packages
apt-get update
apt-get install -y git postgresql-server-dev-9.1 python-dev cmake build-essential libgnutls28-dev uuid-dev gnutls-bin memcached redis-server chrpath git-core libssl-dev libfontconfig1-dev

if [ ! -z "$TRAVIS" ]; then
    PHANTOMJS=phantomjs-1.9.7-linux-i686
    cd /usr/local/share/
    if [ ! -d $PHANTOMJS ]; then
        wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOMJS.tar.bz2
        tar -xjf $PHANTOMJS.tar.bz2
        ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/local/share/phantomjs; sudo ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/local/bin/phantomjs; sudo ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/bin/phantomjs
    fi
    cd $STARTING_DIR
fi

# Set up virtual environment
mkdir -p /var/www/envs
if [ ! -d /var/www/envs/twweb ]; then
    wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    pip install virtualenv
    virtualenv /var/www/envs/twweb
    printf "\n\nsource /var/www/twweb/environment_variables.sh\n" >> /var/www/envs/twweb/bin/activate
    cp /var/www/twweb/scripts/vagrant/environment_variables.sh /var/www/twweb/
fi
if [ ! -L /var/www/twweb/bin ]; then
    ln -s /var/www/envs/twweb/bin /var/www/twweb/bin
fi

source /var/www/twweb/environment_variables.sh
mkdir -p /var/www/twweb/task_data

# Install Taskd and setup certificates
if [ ! -d $TWWEB_TASKD_DATA ]; then
    # See environment variable TWWEB_TASKD_DATA

    mkdir -p $TWWEB_TASKD_DATA/src
    cd $TWWEB_TASKD_DATA/src

    wget http://taskwarrior.org/download/taskd-1.0.0.tar.gz
    tar xzf taskd-1.0.0.tar.gz
    cd taskd-1.0.0

    which taskd
    if [ $? -ne 0 ]; then
        cmake .
        make
        make install
    fi

    cd $TWWEB_TASKD_DATA
    export TASKDDATA=$TWWEB_TASKD_DATA
    taskd init
    taskd add org inthe_am
    cp /var/www/twweb/scripts/vagrant/simple_taskd_upstart.conf /etc/init/taskd.conf

    service taskd stop

    # generate certificates
    cd $TWWEB_TASKD_DATA/src/taskd-1.0.0/pki
    ./generate
    cp client.cert.pem $TASKDDATA
    cp client.key.pem $TASKDDATA
    cp server.cert.pem $TASKDDATA
    cp server.key.pem $TASKDDATA
    cp server.crl.pem $TASKDDATA
    cp ca.cert.pem $TASKDDATA
    cp ca.key.pem $TASKDDATA

    cp /var/www/twweb/scripts/vagrant/simple_taskd_configuration.conf /var/taskd/config
    cp /var/www/twweb/scripts/vagrant/certificate_signing_template.template /var/taskd/cert.template

    sudo chown -R vagrant:vagrant $TASKDDATA

    service taskd start
fi

which task
if [ $? -ne 0 ]; then
    cd $TWWEB_TASKD_DATA/src
    wget http://taskwarrior.org/download/task-2.3.0.tar.gz
    tar xzf task-2.3.0.tar.gz
    cd task-2.3.0
    cmake .
    make
    make install
fi

# Install requirements
source /var/www/envs/twweb/bin/activate
pip install --download-cache=/tmp/pip_cache -r /var/www/twweb/requirements.txt

if [ ! -z "$TRAVIS" ]; then
    pip install ipdb
    python /var/www/twweb/manage.py syncdb --noinput
    python /var/www/twweb/manage.py migrate --noinput

    if [ ! -f /etc/init/taskd-celery.conf ]; then
        cp /var/www/twweb/scripts/vagrant/simple_celery_upstart.conf /etc/init/taskd-celery.conf
        service taskd-celery start
    fi

    service taskd-celery restart
fi
