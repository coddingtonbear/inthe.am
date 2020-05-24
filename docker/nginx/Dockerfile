FROM madnificent/ember:2.18.0 as ember

COPY /ember /app
RUN cd /app && npm install && bower install && ember build

FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/server.conf /etc/nginx/conf.d/server.conf
COPY docker/nginx/server.crt /server.crt
COPY docker/nginx/server.key /server.key

COPY --from=ember /app/dist/ /app

VOLUME /app/logs
