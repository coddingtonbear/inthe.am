FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/conf.d/server.conf

RUN mkdir /app
RUN mkdir /django-static

VOLUME /app
VOLUME /django-static
VOLUME /certificates
