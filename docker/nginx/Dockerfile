FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/conf.d/server.conf
COPY docker/nginx/server.crt /server.crt
COPY docker/nginx/server.key /server.key

RUN mkdir /app

VOLUME /app
VOLUME /app/static
