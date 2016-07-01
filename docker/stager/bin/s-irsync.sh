#!/bin/bash

function print_usage() {

    cat <<EOF
Usage:

  $ s-irsync.sh <src> <dst>

EOF
}

# check if control file is given
if [ $# -lt 2 ]; then
    print_usage
    exit 1
fi

src=$( echo $1 | sed 's/irods:/i:/g' )
dst=$( echo $2 | sed 's/irods:/i:/g' )

cmd="irsync -v -K -r '$src' '$dst'"

echo $cmd

exit 0
