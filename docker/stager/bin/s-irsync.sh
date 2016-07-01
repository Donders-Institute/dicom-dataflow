#!/bin/bash

function print_usage() {

    cat <<EOF
Usage:

  $ s-irsync.sh <src> <dst>

EOF
}

# check if control file is given
if [ $# -ne 2 ]; then
    print_usage
    exit 1
fi

src=$( echo $1 | sed 's/irods:/i:/g' )
dst=$( echo $2 | sed 's/irods:/i:/g' )

## check source type/existence
is_src_dir=0
echo $src | egrep '^i:' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    ils $src > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "file or collection not found: $src" 1>&2
        exit 1
    fi
else
    if [ -e $src ]; then
        if [ -d $src ]; then
            is_src_dir=1
        fi
    else
        echo "file or directory not found: $src" 1>&2
        exit 1
    fi
fi 

## prepare destination directory/collection
is_irods=0
is_dst_dir=0

echo $dst | egrep '^i:' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    is_irods=1
fi 

echo $dst | egrep '.*/$' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    is_dst_dir=1
fi

if [ $is_dst_dir -eq 1 ]; then
    if [ $is_irods -eq 1 ]; then
        imkdir -p "$( echo $dst | sed 's/^i://g')"
    else
        mkdir -p "${dst}"
    fi
fi

if [ $is_src_dir -eq 1 ] && [ $is_dst_dir -ne 1 ] ; then
    echo "cannot rsync directory into file: $src -> $dst" 1>&2
    exit 1
fi

if [ $is_src_dir -eq 1 ] || [ $is_dst_dir -eq 1 ] ; then
    irsync -v -K -r "${src}" "${dst}"
    exit $?
fi
