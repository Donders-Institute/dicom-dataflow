##-- stage: build DCMTK only once
FROM almalinux:9 AS dcmtk-build

ARG dcmtk_prefix=/opt/dcmtk/latest
ENV DCMTK_PREFIX=$dcmtk_prefix

RUN dnf -y install gcc gcc-c++ make cmake curl-minimal tar gzip \
    && dnf clean all \
    && rm -rf /var/cache/dnf/*

RUN mkdir -p /tmp \
    && cd /tmp \
    && curl -LO https://github.com/DCMTK/dcmtk/archive/refs/tags/DCMTK-3.6.4.tar.gz \
    && tar xzf DCMTK-3.6.4.tar.gz \
    && cd dcmtk-DCMTK-3.6.4 \
    && mkdir dcmtk_build \
    && cd dcmtk_build \
    && cmake -DCMAKE_INSTALL_PREFIX="$DCMTK_PREFIX" -DCMAKE_BUILD_TYPE=Release ../ \
    && make -j"$(nproc)" \
    && make install/strip \
    && rm -rf /tmp/*

##-- stage: build tg-toolset-golang
FROM golang:1.25-bookworm as gobuild
ARG tg_toolset_tag=v1.32.0
RUN echo ${tg_toolset_tag} && curl -LO https://github.com/Donders-Institute/tg-toolset-golang/archive/refs/tags/${tg_toolset_tag}.tar.gz && \
    tar xvzf ${tg_toolset_tag}.tar.gz && cd tg-toolset-golang-${tg_toolset_tag#'v'} && GOPATH=/tmp/go make
RUN ls /tmp/go/bin

##-- stage: slim runtime base with dcmtk runtime files only
FROM almalinux:9-minimal AS runtime-base

ARG dcmtk_prefix=/opt/dcmtk/latest
ENV DCMTK_PREFIX=$dcmtk_prefix
ENV PATH=${DCMTK_PREFIX}/bin:${PATH}
ENV LD_LIBRARY_PATH=${DCMTK_PREFIX}/lib64:${LD_LIBRARY_PATH}
ENV DCMDICTPATH=${DCMTK_PREFIX}/share/dcmtk/dicom.dic

RUN microdnf -y install libstdc++ libgcc \
    && microdnf clean all

COPY --from=dcmtk-build ${dcmtk_prefix} ${dcmtk_prefix}

##-- stage: build cal2wl container
FROM runtime-base AS cal2wl

MAINTAINER Donders Institute
LABEL donders.ru.nl.app_name "dicomdf-cal2wl"
LABEL donders.ru.nl.app_maintainer "h.lee@donders.ru.nl"
LABEL donders.ru.nl.app_code_repository "https://github.com/Donders-Institute/dicom-dataflow"

RUN microdnf -y install cronie \
    && microdnf clean all

ENV WLBROKER_DIR=/data/wlbroker/WLBROKER

COPY --from=gobuild /tmp/go/bin/dicom_worklist /usr/local/bin

COPY cal2wl/cron/crontab /cron/crontab
COPY cal2wl/cron/*.sh /cron/
RUN chmod +x /cron/*.sh

VOLUME [ "/data/wlbroker", "/data/log", "/opt/config" ]

COPY cal2wl/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

##-- stage: build wlbroker
FROM runtime-base AS wlbroker

ENV WLBROKER_DATADIR=/data/wlbroker
COPY wlbroker/entrypoint.sh entrypoint.sh
RUN (chmod +x entrypoint.sh)

VOLUME ["/data/wlbroker"]
EXPOSE 1234

ENTRYPOINT ["./entrypoint.sh"]

##-- stage: build ORTHANC server
FROM jodogne/orthanc:1.4.2 AS orthanc

COPY orthanc/scripts/* /var/lib/orthanc/scripts/

VOLUME [ "/var/lib/orthanc/log", "/var/lib/orthanc/db", "/var/lib/orthanc/idx", "/var/lib/orthanc/etc" ]
EXPOSE 4242
EXPOSE 8042

ENV STREAMER_URL="http://streamer:3001"

WORKDIR /var/lib/orthanc
ENTRYPOINT [ "Orthanc", "--logdir=/var/lib/orthanc/log", "/var/lib/orthanc/etc" ]
