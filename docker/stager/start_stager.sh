#!/bin/bash

cat irods_otp | iinit
$NODEJS_PREFIX/bin/node stager.js
