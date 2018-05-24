#!/bin/bash

function echo_help {
    echo
    echo "USAGE: $0 [-h] [-f]"
    echo 
    echo "  -h  : this help"
    echo "  -s  : skip git checkout packages from Donders-Institute github, such as hpc-utility, etc."
    echo "  -f  : start a fresh container. Data on existing volumes will be erased"
    echo 
}

fresh=0
skiptar=0
branch=master
while getopts "hfs" opt; do
    case $opt in 
        h)
            echo_help
            exit 0
            ;;
        f)
            fresh=1
            ;;
        s)
            skiptar=1
            ;;
        \?)
            echo_help
            exit 1
    esac
done

## download hpc-utility package
if [ $skiptar -eq 0 ]; then
    echo -n 'github username (for Donders-Institute/hpc-utility): '
    read gituser

    curl -u ${gituser} -LOk https://github.com/Donders-Institute/hpc-utility/archive/${branch}.zip

    if [ $? -ne 0 ]; then
        echo "Cannot checkout hpc-utility repository." 1>&2
    fi

    unzip ${branch}.zip && rm -f ${branch}.zip
    mv hpc-utility-${branch} hpc-utility \
    && tar cvf hpc-utility.tar hpc-utility \
    && gzip hpc-utility.tar \
    && rm -rf hpc-utility \
    && mv -f hpc-utility.tar.gz ./base
fi

## refresh volumes
if [ $fresh -eq 1 ]; then
    vols=(vol-orthanc-log vol-orthanc-db vol-orthanc-idx vol-wlbroker)
    for v in ${vols[*]}; do
        docker volume ls | grep ${v} 2>&1 > /dev/null
        if [ $? -eq 0 ]; then echo -n 'remove volume '; docker volume rm ${v}; fi
        echo -n 'create volume '; docker volume create ${v} 
    done
fi

docker network ls | grep nw-dicom-dataflow 2>&1 > /dev/null
if [ $? -ne 0 ]; then
    echo -n 'create volume '; docker network create nw-dicom-dataflow
fi

## build containers
docker-compose build --force-rm
## shutdown existing containers
docker-compose down
## start new containers
docker-compose up -d
