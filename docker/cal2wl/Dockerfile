# stage 1: build tg-toolset-golang for the binary dicom_worklist
FROM golang:1.16 as gobuild
ARG TG_TOOLSET_TAG=1.9.0
RUN curl -LO https://github.com/Donders-Institute/tg-toolset-golang/archive/refs/tags/${TG_TOOLSET_TAG}.tar.gz && \
    tar xvzf ${TG_TOOLSET_TAG}.tar.gz && cd tg-toolset-golang-${TG_TOOLSET_TAG} && GOPATH=/tmp/go make
RUN ls /tmp/go/bin

# stage 2: build cal2wl container
FROM ${DOCKER_REGISTRY:-dccn}/dicomdf-base:${DOCKER_IMAGE_TAG:-latest}

# application metadata
MAINTAINER Donders Institute
LABEL donders.ru.nl.app_name "dicomdf-cal2wl"
LABEL donders.ru.nl.app_maintainer "h.lee@donders.ru.nl"
LABEL donders.ru.nl.app_code_repository "https://github.com/Donders-Institute/dicom-dataflow"

# install system cron
RUN ( yum -y install cronie crontabs )

# additional environment variables
ENV WLBROKER_DIR=/data/wlbroker/WLBROKER

# copy dicom_worklist go binary from gobuild
COPY --from=0 /tmp/go/bin/dicom_worklist /usr/local/bin

# copy the crontab and exec scripts for the cron jobs
COPY cron/crontab /cron/crontab
COPY cron/*.sh /cron/
RUN chmod +x /cron/*.sh

# add crontab to the user
RUN crontab /cron/crontab

# prepare system env for cron runtime
RUN ( echo "export DCMTK_PREFIX=$DCMTK_PREFIX" > /cron/env.sh )
RUN ( echo "export WLBROKER_DIR=$WLBROKER_DIR" >> /cron/env.sh )

# shared volumes
VOLUME [ "/data/wlbroker", "/data/log", "/opt/config" ]

# start the cron
CMD /usr/sbin/crond -m off -n -p
