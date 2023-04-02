ARG base_image=dccn/dicomdf-base:latest
# stage 1: build tg-toolset-golang for the binary dicom_worklist
FROM golang:1.20 as gobuild
ARG tg_toolset_tag=latest
RUN echo ${tg_toolset_tag} && curl -LO https://github.com/Donders-Institute/tg-toolset-golang/archive/refs/tags/${tg_toolset_tag}.tar.gz && \
    tar xvzf ${tg_toolset_tag}.tar.gz && cd tg-toolset-golang-${tg_toolset_tag#'v'} && GOPATH=/tmp/go make
RUN ls /tmp/go/bin

# stage 2: build cal2wl container
FROM $base_image

# application metadata
MAINTAINER Donders Institute
LABEL donders.ru.nl.app_name "dicomdf-cal2wl"
LABEL donders.ru.nl.app_maintainer "h.lee@donders.ru.nl"
LABEL donders.ru.nl.app_code_repository "https://github.com/Donders-Institute/dicom-dataflow"

# install system cron
RUN (ulimit -n 1024 && yum -y install cronie && yum clean all && rm -rf /var/cache/yum/*)

# additional environment variables
ENV WLBROKER_DIR=/data/wlbroker/WLBROKER

# copy dicom_worklist go binary from gobuild
COPY --from=0 /tmp/go/bin/dicom_worklist /usr/local/bin

# copy the crontab and exec scripts for the cron jobs
COPY cron/crontab /cron/crontab
COPY cron/*.sh /cron/
RUN chmod +x /cron/*.sh

# shared volumes
VOLUME [ "/data/wlbroker", "/data/log", "/opt/config" ]

# entrypoint
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
