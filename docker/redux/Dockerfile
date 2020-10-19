FROM node:12.19.0-alpine3.11 as node

COPY /ui /app

RUN cd /app && npm install

WORKDIR /app

VOLUME /app

RUN mkdir -p /dist
VOLUME /dist

ENV BUILD_MODE=development
CMD node_modules/.bin/webpack --watch --mode $BUILD_MODE
