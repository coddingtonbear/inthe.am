FROM python:3.8-slim

ENV TASKDDATA=/var/taskd USERNAME=taskd CA_CERT=/var/taskd/pki/ca.cert.pem \
  CA_KEY=/var/taskd/pki/ca.key.pem CA_SIGNING_TEMPLATE=/var/taskd/cert.template

RUN apt-get update
RUN apt-get install -y build-essential git supervisor uuid-dev cmake libpq-dev \
  postgresql-server-dev-11 libgnutls28-dev gnutls-bin
RUN git clone https://github.com/coddingtonbear/taskserver
RUN cd taskserver &&\
  git checkout inthe_am.dockerized &&\
  cmake -DCMAKE_INSTALL_PREFIX=/usr &&\
  make && make install

COPY docker/taskd/simple_taskd_configuration.conf /var/taskd/config
COPY docker/taskd/certificate_signing_template.template /var/taskd/cert.template
COPY docker/taskd/entrypoint.sh /app/run.sh
COPY docker/taskd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY taskd_services/http/api.py /app/api.py
COPY taskd_services/http/requirements.txt /tmp/requirements.txt

RUN chown ${USER_NAME}:${USER_NAME} ${TASKDDATA}
RUN chown ${USER_NAME}:${USER_NAME} /tmp/

RUN pip install --no-cache -r /tmp/requirements.txt

# Configure container
VOLUME ["${TASKDDATA}"]
EXPOSE 53589
EXPOSE 80
ENTRYPOINT /usr/bin/supervisord --nodaemon

USER ${USER_NAME}
