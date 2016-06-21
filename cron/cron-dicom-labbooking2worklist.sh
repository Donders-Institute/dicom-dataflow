#!/bin/bash

source /opt/_modules/setup.sh
module load python
module load cluster 
module load dcmtk
source $CLUSTER_UTIL_ROOT/share/cluster-lib.sh
cwd=$( get_script_dir $0 )

export DCCN_PYTHONDIR=/opt/python/dccn

WLBROKER_DIR=/scratch/data/wlbroker/WLBROKER

today=$( date +%Y-%m-%d )
#today=2016-06-01

$DCCN_PYTHONDIR/bin/dicom-labbooking2worklist.py -c ${cwd}/cron-dicom-labbooking2worklist.ini -d $today -s $WLBROKER_DIR
