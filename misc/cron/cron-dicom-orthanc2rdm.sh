#!/bin/bash

ts_now=$( date +%s )

# this script takes three arguments:
# 1. The "time_offset" to be passed on to ../bin/orthanc_getstudies.py
#    This argument indicates how far in the past from this script's execution time the studies should considered.
# 2. The "rdm_coll_ns" to be passed on to ../bin/orthanc_getarchive.py
#    This argument specifies to which RDM collection the study archives should be uploaded.
module load python
module load irods 

# find out the directory in which this script is stored
SOURCE=$0
# resolve $SOURCE until the file is no longer a symlink
while [ -h "$SOURCE" ]; do
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# retrive new studies
ts_offset=$1
ts_from=$(( ts_now - 3600 * ts_offset ))

dt_from=$( date -d @${ts_from} +'%Y-%m-%d %H:%M:%S' )
dt_to=$( date -d @${ts_now} +'%Y-%m-%d %H:%M:%S' )

#orthanc_get_studies.py list -t "$dt_to" -f "$dt_from"
#TODO: find a better way to deal with studies that are not "stable"
studies=( `orthanc_get_studies.py list -c $DIR/cron-dicom-orthanc2rdm.ini -t "$dt_to" -f "$dt_from"` )

# load studies for retry
F_RETRY=$DIR/log/orthanc2rdm.retry
if [ -f $F_RETRY ]; then
    for s in $( cat $F_RETRY | awk -F '|' '{print $2}' | sort | uniq ); do
        studies+=($s)
    done
fi

# resolve unique studies to be archives
unique_studies=( $(echo "${studies[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ') )

if [ ${#unique_studies[@]} -gt 0 ]; then
    cmd="rdm-upload-dicom-studies.py --config $DIR/config.ini --rdm-coll-ns $2 --rdm-imode icommands --rdm-datadir-rel raw"
    for s in "${unique_studies[@]}"; do
        cmd="$cmd $s"
    done

    # catch failure in temporary file
    TMP_ERR=$DIR/log/rdm-upload-dicom-studies.err.$$
    $cmd 2>$TMP_ERR

    # resolve the failed studies by parsing the temporary error file
    grep -e '^0|' $TMP_ERR > $F_RETRY
else
    echo "nothing to archive" 1>&2
fi
