#!/bin/bash

export PATH=$DCMTK_PREFIX/bin:$PATH

today=$( date +%Y-%m-%d )
#today=2016-06-01

[ ! -d $WLBROKER_DIR ] && mkdir -p $WLBROKER_DIR

/usr/local/bin/dicom_worklist generate prisma prismafit skyra -c /opt/config/config.yml -d $today -p $WLBROKER_DIR