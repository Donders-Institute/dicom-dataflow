#!/bin/sh

## copy required environment variables for cron jobs
echo "DCMTK_PREFIX=$DCMTK_PREFIX" > /etc/environment
echo "WLBROKER_DIR=$WLBROKER_DIR" >> /etc/environment

## replace with customized crontab
if [ -f /cron/crontab ]; then
    cat /cron/crontab > /var/spool/cron/root
    ## make sure the crontab is in mode 0600
    chmod 0600 /var/spool/cron/root
fi

## print out the content of the crontab
cat /var/spool/cron/root

## start crond in foreground
crond -n