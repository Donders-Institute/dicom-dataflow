#!/bin/bash

src=/project/3010000.03/raw/mri/SUBJ0003/
dst=$( echo $src | sed 's|/project|irods:/rdm/di/dccn/DAC_3010000.01_173|g' )
now=$( date )

curl -H "Content-Type: application/json" -X POST -d \
"{ \"type\": \"rdm\",
   \"data\": { \"srcURL\": \"${src}\",
               \"dstURL\": \"${dst}\",
               \"title\": \"[${now}] push to ${dst}\"},
   \"options\": { \"attempts\": 3,
                  \"backoff\": { \"delay\": 60000, \"type\": \"fixed\" }}
 }" http://localhost:3000/job
