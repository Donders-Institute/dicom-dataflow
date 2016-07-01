#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: $0 <irods-tag>" 
    exit 1
fi

# build distributable icommands tarball
tag=$1
git clone -b $tag --single-branch https://github.com/irods/irods.git irods-${tag}

cd irods-${tag}

git submodule init
git submodule update

./packaging/build.sh -r icommands

# install RPM package
rpm -ivh ./build/irods-icommands-${tag}-64bit-centos7.rpm

# remove source code
cd ..
rm -rf irods-${tag}
