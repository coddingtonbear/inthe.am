FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/conf.d/server.conf

RUN mkdir /app

VOLUME /app
VOLUME /app/static
VOLUME /certificates
