FROM alpine:3.11

ENV TASKD_VERSION=1.1.0-r6 \
 TASKDDATA=/var/taskd \
 USER_NAME=twtaskd

RUN apk -U --no-cache upgrade && \
  apk -U --no-cache add taskd=${TASKD_VERSION} taskd-pki=${TASKD_VERSION}

COPY simple_taskd_configuration.conf /var/taskd/config
COPY certificate_signing_template.template /var/taskd/cert.template
COPY entrypoint.sh /app/run.sh
# TODO accept userid from build-arg
RUN addgroup -g 1000 -S ${USER_NAME} && \
    adduser -u 1000 -S ${USER_NAME} -G ${USER_NAME}
USER ${USER_NAME}
# Configure container
VOLUME ["${TASKDDATA}"]
EXPOSE 53589
ENTRYPOINT ["/app/run.sh"]
