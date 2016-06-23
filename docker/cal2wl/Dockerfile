FROM dccn-dicomdf-base

# additional environment variables
ENV WLBROKER_DIR=/data/wlbroker/WLBROKER

# shared volumes
VOLUME [ "/cron", "/data/wlbroker", "/opt/config.ini" ]

# start the cron
CMD $PYTHON_PREFIX/bin/devcron.py /cron/crontab
