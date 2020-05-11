FROM madnificent/ember:2.18.0 as ember

COPY . /app
WORKDIR /app
RUN cd /app && npm install
# RUN cd /app && ls -la ; ls -la bower_components/font-awesome/
# RUN cd /app ; ln -s bower_components/font-awesome/{otfs,fonts} &&
RUN bower install
RUN ember build
CMD ["ember", "server"]
