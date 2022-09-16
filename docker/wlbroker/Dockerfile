ARG base_image=dccn/dicomdf-base:latest
FROM $base_image

# install wlbroker starter script
ENV WLBROKER_DATADIR=/data/wlbroker
COPY entrypoint.sh entrypoint.sh
RUN (chmod +x entrypoint.sh)

# worklist data store and service port
VOLUME ["/data/wlbroker"]
EXPOSE 1234

ENTRYPOINT ["./entrypoint.sh"]
