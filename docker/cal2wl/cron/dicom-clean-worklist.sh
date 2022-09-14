#!/bin/bash

today=$( date +%Y-%m-%d )

for f in $( find $WLBROKER_DIR -type f -not -name "*_${today}*" | grep -v lockfile | grep '\.wl' ); do
    rm -f $f
done

# clean up *.dump files older than 14 days
find /mnt/docker/data/wlbroker/WLBROKER -name '*.dump' -mtime +14 -exec rm {} \;