#!/bin/bash

export PATH=$PYTHON_PREFIX/bin:$DCMTK_PREFIX/bin:$PATH

today=$( date +%Y-%m-%d )
#today=2016-06-01

$DCCN_PYTHONDIR/bin/dicom-labbooking2worklist.py -c /opt/config/config.ini -d $today -s $WLBROKER_DIR
