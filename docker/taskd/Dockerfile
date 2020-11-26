FROM python:3.8-slim

ENV TASKDDATA=/var/taskd CA_CERT=/var/taskd/pki/ca.cert.pem \
  CA_KEY=/var/taskd/pki/ca.key.pem CA_SIGNING_TEMPLATE=/var/taskd/cert.template \
  REDIS_HOST=redis CERTIFICATE_DB=/var/taskd/orgs/certificates.sqlite3

RUN apt-get update
RUN apt-get install -y build-essential git supervisor uuid-dev cmake \
  libgnutls28-dev gnutls-bin libev-dev libhiredis-dev libjsoncpp-dev \
  libsqlite3-dev
# This is the library used for communicating with Redis
RUN git clone https://github.com/hmartiro/redox &&\
  cd redox &&\
  cmake . &&\
  make && make install &&\
  mv /usr/local/lib64/* /usr/lib/x86_64-linux-gnu
# & install the taskserver itself
RUN git clone https://github.com/coddingtonbear/taskserver &&\
  cd taskserver &&\
  git checkout inthe_am_dockerized &&\
  cmake \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DREDOX_INCLUDE_DIR=../redox/include &&\
  make && make install

COPY docker/taskd/simple_taskd_configuration.conf /var/taskd/config
COPY docker/taskd/certificate_signing_template.template /var/taskd/cert.template
COPY docker/taskd/entrypoint.sh /app/run.sh
COPY docker/taskd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY taskd_services/http/api.py /app/api.py
COPY taskd_services/http/requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /var/taskd/orgs
VOLUME /var/taskd/orgs

RUN mkdir -p /var/taskd/pki
VOLUME /var/taskd/pki

EXPOSE 53589
EXPOSE 8000
CMD /usr/bin/supervisord --nodaemon
