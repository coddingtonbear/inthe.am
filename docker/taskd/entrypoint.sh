#!/bin/sh
export LOCAL_IP=`getent hosts web | awk '{ print $1 }'`

if [ ! -d $TASKDDATA ]; then
    echo "Task data is not mounted!"
    exit 1
fi
if [ ! -f ${TASKDDATA}/pki/generated ]; then
    echo "Generating taskdata configuration..."
    cd $TASKDDATA
    taskd init
    taskd add org inthe_am
    taskd add org testing

    touch ${TASKDDATA}/pki/generated
    cp /taskserver/pki/generate* ${TASKDDATA}/pki
    cp /taskserver/pki/vars ${TASKDDATA}/pki
    cd ${TASKDDATA}/pki
    ./generate
    taskd config --force client.cert ${TASKDDATA}/pki/client.cert.pem
    taskd config --force client.key ${TASKDDATA}/pki/client.key.pem
    taskd config --force server.cert ${TASKDDATA}/pki/server.cert.pem
    taskd config --force server.key ${TASKDDATA}/pki/server.key.pem
    taskd config --force server.crl ${TASKDDATA}/pki/server.crl.pem
    taskd config --force ca.cert ${TASKDDATA}/pki/ca.cert.pem

    # And finaly set taskd to listen in default port
    taskd config --force server 0.0.0.0:53589

    # Configure database settings for looking up account information
    taskd config --force intheam.min_tos 1
    taskd config --force intheam.min_privacy 1
else
    echo "Taskdata configuration already generated, skipping"
fi
/usr/bin/taskd server --log=-
