FROM dccn-dicomdf-base

# additional environment variables
ENV WLBROKER_DIR=/data/wlbroker/WLBROKER

# copy the WorklistItem.py into the DCCN PYTHON library path
COPY python/WorklistManager.py /opt/hpc-utility/python/lib/orthanc/

# copy the dicom-labbooking2worklist.py into the DCCN PYTHON bin path
COPY python/dicom-labbooking2worklist.py /opt/hpc-utility/python/bin/
RUN chmod +x /opt/hpc-utility/python/bin/dicom-labbooking2worklist.py

# copy the crontab and exec scripts for the cron jobs
COPY cron/crontab /cron/crontab
COPY cron/*.sh /cron/
RUN chmod +x /cron/*.sh

# shared volumes
VOLUME [ "/data/wlbroker", "/opt/config" ]

# start the cron
CMD $PYTHON_PREFIX/bin/devcron.py /cron/crontab
