#!/bin/sh
#
# wlserver	This script starts a DICOM worklist server
#

TCP_PORT=1234
WLDIR=${WLBROKER_DATADIR}
DICOM_MODALITY=WLBROKER
MODALITY_DIR=${WLDIR}/${DICOM_MODALITY}
LOG_DIR=${WLBROKER_DATADIR}/log

# load dcmtk
export PATH=${DCMTK_PREFIX}/bin:$PATH
export LD_LIBRARY_PATH=${DCMTK_PREFIX}/lib64:$LD_LIBRARY_PATH
export DCMDICTPATH=${DCMTK_PREFIX}/share/dcmtk/dicom.dic

# let see how we were called
echo -n "Starting DICOM worklist server: "
if [ ! -d ${MODALITY_DIR} ]; then
    mkdir -p ${MODALITY_DIR}
    touch ${MODALITY_DIR}/lockfile
fi

if [ ! -d ${LOG_DIR} ]; then
    mkdir -p ${LOG_DIR}
fi

wlmscpfs -v -dfp $WLDIR -dfr $TCP_PORT > $LOG_DIR/wlbroker.log 2>&1
