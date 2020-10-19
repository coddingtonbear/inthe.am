FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/conf.d/server.conf

RUN mkdir /app
COPY docker/nginx/index.html /app/index.html

RUN mkdir /django-static

VOLUME /app/dist
VOLUME /django-static
VOLUME /certificates
