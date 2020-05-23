FROM madnificent/ember:2.18.0 as ember

COPY . /app
RUN cd /app && npm install && bower install && ember build

FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default
COPY docker/sites-enabled/ /etc/nginx/sites-enabled

COPY --from=ember /app/dist/ /app

VOLUME /app/logs
