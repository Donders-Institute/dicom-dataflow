#!/bin/bash

for i in `seq 1 10`; do
    curl -H "Content-Type: application/json" -X POST -d \
    "{ \"type\": \"rdm\",
       \"data\": { \"srcURL\": \"/project/3010000.01/raw/mri/SUBJ${i}\",
                   \"dstURL\": \"irods:/rdm/di/dccn/DAC_3010000.01/raw/mri/SUBJ${i}\" },
       \"options\": { \"attempts\": 3,
                      \"backoff\": { \"delay\": 60000, \"type\": \"fixed\" }}
     }" http://localhost:3000/job

done
