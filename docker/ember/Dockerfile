FROM madnificent/ember:2.18.0 as ember

COPY /ember /app
RUN cd /app && npm install -g && bower install -g

WORKDIR /app

VOLUME /app

RUN mkdir -p /dist
VOLUME /dist

ENTRYPOINT ember build --watch --output-path=/dist
