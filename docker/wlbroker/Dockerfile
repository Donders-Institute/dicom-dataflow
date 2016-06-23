FROM dccn-dicomdf-base

# install wlbroker starter script
ENV WLBROKER_DATADIR=/data/wlbroker
COPY wlbroker.sh wlbroker.sh
RUN (chmod +x wlbroker.sh)

# worklist data store and service port
VOLUME [ "/data/wlbroker" ]
EXPOSE 1234

CMD [ "./wlbroker.sh" ]
