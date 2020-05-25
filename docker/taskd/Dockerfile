FROM python:3.8-slim

ENV TASKDDATA=/var/taskd USERNAME=taskd

RUN apt-get update
RUN apt-get install -y build-essential git supervisor uuid-dev cmake libpq-dev \
  postgresql-server-dev-11 libgnutls28-dev gnutls-bin
RUN git clone https://github.com/coddingtonbear/taskserver
RUN cd taskserver &&\
  cmake -DCMAKE_INSTALL_PREFIX=/usr &&\
  make && make install

COPY docker/taskd/simple_taskd_configuration.conf /var/taskd/config
COPY docker/taskd/certificate_signing_template.template /var/taskd/cert.template
COPY docker/taskd/entrypoint.sh /app/run.sh
COPY docker/taskd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN chown ${USER_NAME}:${USER_NAME} ${TASKDDATA}
RUN chown ${USER_NAME}:${USER_NAME} /tmp/

# Configure container
VOLUME ["${TASKDDATA}"]
EXPOSE 53589
CMD ["/usr/bin/supervisord"]

USER ${USER_NAME}
