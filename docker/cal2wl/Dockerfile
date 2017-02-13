FROM dccn-dicomdf-base

# application metadata
MAINTAINER Donders Institute
LABEL donders.ru.nl.app_name "dicomdf-cal2wl"
LABEL donders.ru.nl.app_maintainer "h.lee@donders.ru.nl"
LABEL donders.ru.nl.app_code_repository "https://github.com/Donders-Institute/dicom-dataflow"

# install system cron
RUN ( yum -y install cronie crontabs )

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

# add crontab to the user
RUN crontab /cron/crontab

# prepare system env for cron runtime
RUN ( echo "export DCMTK_PREFIX=$DCMTK_PREFIX" > /cron/env.sh )
RUN ( echo "export PYTHON_PREFIX=$PYTHON_PREFIX" >> /cron/env.sh )
RUN ( echo "export WLBROKER_DIR=$WLBROKER_DIR" >> /cron/env.sh )
RUN ( echo "export DCCN_PYTHONDIR=$DCCN_PYTHONDIR" >> /cron/env.sh )

# shared volumes
VOLUME [ "/data/wlbroker", "/data/log", "/opt/config" ]

# start the cron
#CMD $PYTHON_PREFIX/bin/devcron.py /cron/crontab
CMD /usr/sbin/crond -m off -n -p
