#!/bin/bash
set -x
set -e

STARTING_DIR=$(pwd)
MAIN_DIR=/var/www/twweb
if [ ! -z "$TRAVIS" ]; then
    MAIN_DIR=$STARTING_DIR
fi

# Install necessary packages
echo "installing depencencies"
apt-get update
apt-get install -y python-software-properties
apt-add-repository -y ppa:chris-lea/node.js
apt-get update
apt-get install -y git postgresql-server-dev-9.1 python-dev cmake build-essential uuid-dev gnutls-bin memcached redis-server chrpath git-core libssl-dev libfontconfig1-dev nodejs firefox checkinstall curl libcurl4-gnutls-dev libgnutls-dev libxml2-dev libxslt1-dev

# Python prerequisites
wget -nv https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install virtualenv
pip install wheel

if [ -z "$TRAVIS" ]; then
    PHANTOMJS=phantomjs-1.9.7-linux-i686
    echo "installing $PHANTOMJS"
    cd /usr/local/share/
    if [ ! -d $PHANTOMJS ]; then
        wget -nv https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOMJS.tar.bz2
        tar -xjf $PHANTOMJS.tar.bz2
        ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/local/share/phantomjs; sudo ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/local/bin/phantomjs; sudo ln -s /usr/local/share/$PHANTOMJS/bin/phantomjs /usr/bin/phantomjs
    fi
    cd $STARTING_DIR

    # Increase watch count
    echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

    # Set up virtual environment
    echo "setting up virtualenv"
    mkdir -p /var/www/envs
    if [ ! -d /var/www/envs/twweb ]; then
        virtualenv /var/www/envs/twweb
        printf "\n\nsource $MAIN_DIR/environment_variables.sh\n" >> /var/www/envs/twweb/bin/activate
        cp $MAIN_DIR/scripts/vagrant/environment_variables.sh $MAIN_DIR
    fi
    if [ ! -L $MAIN_DIR/bin ]; then
        ln -s /var/www/envs/twweb/bin $MAIN_DIR/bin
    fi

    # Copy bash profile into place
    cp $MAIN_DIR/scripts/vagrant/bash_profile /home/vagrant/.profile

    source $MAIN_DIR/environment_variables.sh
    source /var/www/envs/twweb/bin/activate
else
    source $MAIN_DIR/scripts/vagrant/environment_variables.sh
    source ~/virtualenv/python2.7/bin/activate
fi

mkdir -p $MAIN_DIR/task_data
mkdir -p $MAIN_DIR/logs

# Install Taskd and setup certificates
if [ ! -d $TWWEB_TASKD_DATA ]; then
    # See environment variable TWWEB_TASKD_DATA

    TASKD_VERSION="taskd-1.0.0"
    echo "installing $TASKD_VERSION and setup certificates"
    mkdir -p $TWWEB_TASKD_DATA/src
    cd $TWWEB_TASKD_DATA/src

    wget -nv http://taskwarrior.org/download/$TASKD_VERSION.tar.gz
    tar xzf $TASKD_VERSION.tar.gz
    cd $TASKD_VERSION

    set +e
    which taskd; RETVAL=$?
    set -e
    if [ $RETVAL -ne 0 ]; then
        cmake .
        make
        checkinstall --default
        cp  /var/taskd/src/$TASKD_VERSION/*.deb /tmp
    fi

    cd $TWWEB_TASKD_DATA
    export TASKDDATA=$TWWEB_TASKD_DATA
    taskd init
    taskd add org inthe_am
    taskd add org testing
    cp $MAIN_DIR/scripts/vagrant/simple_taskd_upstart.conf /etc/init/taskd.conf

    if [ -z "$TRAVIS" && -z "`pgrep -x taskd`" ]; then
        service taskd stop
    fi

    # generate certificates
    cd $TWWEB_TASKD_DATA/src/$TASKD_VERSION/pki
    ./generate
    cp client.cert.pem $TASKDDATA
    cp client.key.pem $TASKDDATA
    cp server.cert.pem $TASKDDATA
    cp server.key.pem $TASKDDATA
    cp server.crl.pem $TASKDDATA
    cp ca.cert.pem $TASKDDATA
    cp ca.key.pem $TASKDDATA

    cp $MAIN_DIR/scripts/vagrant/simple_taskd_configuration.conf /var/taskd/config
    cp $MAIN_DIR/scripts/vagrant/certificate_signing_template.template /var/taskd/cert.template

    if [ -z "$TRAVIS" ]; then
        service taskd start
    fi

    set +e
    which task; RETVAL=$?
    set -e
    if [ $RETVAL -ne 0 ]; then
        TASK_VERSION="task-2.3.0"
        echo "installing $TASK_VERSION"
        cd $TWWEB_TASKD_DATA/src
        wget -nv http://taskwarrior.org/download/$TASK_VERSION.tar.gz
        tar xzf $TASK_VERSION.tar.gz
        cd $TASK_VERSION
        cmake .
        make
        checkinstall --default
        cp /var/taskd/src/$TASK_VERSION/*.deb /tmp
    fi
fi

cd $MAIN_DIR
set +e
echo "installing ember-cli and bower"
npm install npm@2.5.1
npm install node@5.0.0
npm install -g ember-cli@2.4.3 bower@1.7.6
echo "running npm install"
npm install
echo "running bower install"
bower --config.interactive=false install --allow-root
set -e
echo "running ember build"
ember build

# Install requirements
echo "installing python requirements"
pip install --download-cache=/tmp/pip_cache -r $MAIN_DIR/requirements.txt

if [ -z "$TRAVIS" ]; then
    echo "preparing application"
    pip install ipdb
    python $MAIN_DIR/manage.py syncdb --noinput
    python $MAIN_DIR/manage.py migrate --noinput

    if [ ! -f /etc/init/taskd-celery.conf ]; then
        cp $MAIN_DIR/scripts/vagrant/simple_celery_upstart.conf /etc/init/taskd-celery.conf
        service taskd-celery start
    fi

    service taskd-celery restart
    service taskd restart
else
    if [ -d /home/travis/.config ]; then
        chmod -R 777 /home/travis/.config
    fi
fi
