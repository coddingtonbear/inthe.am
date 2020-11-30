FROM node:12.19.0-alpine3.11 as node

COPY /ui /app

RUN apk update && apk add --no-cache supervisor

WORKDIR /app

VOLUME /app

RUN mkdir -p /dist
VOLUME /dist

COPY /docker/static-builder/supervisord.conf /etc/supervisord.conf

CMD npm install && /usr/bin/supervisord --nodaemon -c /etc/supervisord.conf
