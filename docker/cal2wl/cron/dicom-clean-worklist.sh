#!/bin/bash

today=$( date +%Y-%m-%d )

for f in $( find $WLBROKER_DIR -type f -not -name "*_${today}*" | grep -v lockfile | grep '\.wl' ); do
    rm -f $f
done
