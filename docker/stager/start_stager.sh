#!/bin/bash

cat irods_otp | iinit

export PATH=$PYTHON_BINDIR:$PATH
$NODEJS_PREFIX/bin/node stager.js
