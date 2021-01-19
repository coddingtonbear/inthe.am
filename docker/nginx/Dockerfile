FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/templates/server.conf.template

RUN mkdir /app
RUN mkdir /django-static
RUN mkdir /certificates

VOLUME /app
VOLUME /django-static
VOLUME /certificates
