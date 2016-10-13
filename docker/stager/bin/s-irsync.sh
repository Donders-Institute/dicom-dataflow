#!/bin/bash

function print_usage() {

    cat <<EOF
Usage:

  $ s-irsync.sh <src> <dst>

EOF
}

function get_script_dir() {

    ## resolve the base directory of this executable
    local SOURCE=$1
    while [ -h "$SOURCE" ]; do
        # resolve $SOURCE until the file is no longer a symlink
        DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$(readlink "$SOURCE")"

        # if $SOURCE was a relative symlink,
        # we need to resolve it relative to the path
        # where the symlink file was located

        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
    done

    echo "$( cd -P "$( dirname "$SOURCE" )" && pwd )"
}

# check if control file is given
if [ $# -ne 2 ]; then
    print_usage
    exit 1
fi

mydir=$( get_script_dir $0 )
rdm_user=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['userName'])" )
rdm_pass=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['userPass'])" )

export IRODS_AUTHENTICATION_FILE=/tmp/.irodsA.$$
export IRODS_USER_NAME=$rdm_user

echo $rdm_pass | iinit > /dev/null 2>&1

src=$( echo $1 | sed 's/irods:/i:/g' )
dst=$( echo $2 | sed 's/irods:/i:/g' )

w_total=0

## check source type/existence
is_src_dir=0
echo $src | egrep '^i:' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    src_coll=$( echo $src | sed 's/^i://' | sed 's/\/$//' )
    ils $src_coll > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "file or collection not found: $src_coll" 1>&2
        exit 1
    fi

    # TODO: find a better way to determine the source is a collection or a data object
    ils ${src_coll}/ > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        is_src_dir=1
        # determine size of the sync task: number of data objects in the source collection 
        w_total=$( iquest --no-page "n=%s" "select UNIQUE(DATA_NAME) where COLL_NAME = '${src_coll}'" | grep 'n=' | wc -l )
        w_total=$(( $w_total + $(iquest --no-page "n=%s" "select UNIQUE(DATA_NAME) where COLL_NAME like '${src_coll}/%'" | grep 'n=' | wc -l) ))
    else
        w_total=1
    fi 
else
    if [ -e $src ]; then
        if [ -d $src ]; then
            is_src_dir=1
            # determine size of the sync task: number of files in the directory 
            w_total=$( find $src -type f | wc -l )
        else
            w_total=1
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
    dst_coll=$( echo $dst | sed 's/^i://' )
    # TODO: find a better way to determine whether the irods namespace is existing and whether it's a directory
    ils ${dst_coll} > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        ils ${dst_coll}/ > /dev/null 2>&1
        # this is an existing irods collection
        if [ $? -eq 0 ]; then
            is_dst_dir=1
        fi
    else
        # the namespace doesn't exist at all, whether it should be a directory is determined by is_src_dir
        is_dst_dir=$is_src_dir
    fi
else
    if [ -e $dst ]; then
        if [ -d $dst ]; then
            is_dst_dir=1
        fi
    else
        is_dst_dir=$is_src_dir
    fi
fi

if [ $is_src_dir -eq 1 ] && [ $is_dst_dir -ne 1 ] ; then
    echo "cannot rsync directory into file: $src -> $dst" 1>&2
    exit 1
fi

# make sure the dst_dir is created
if [ $is_dst_dir -eq 1 ]; then
    if [ $is_irods -eq 1 ]; then
        imkdir -p "$( echo $dst | sed 's/^i://' )" > /dev/null 2>&1
    else
        mkdir -p "${dst}"
    fi
fi

# reconstruct the dst w/ proper filename
if [ $is_src_dir -eq 0 ] && [ $is_dst_dir -eq 1 ] ; then
    fname=$( echo $src | awk -F '/' '{print $NF}' )
    dst=${dst}/${fname}
fi

# run irsync 
if [ $w_total -gt 0 ]; then
    w_done=0
    w_done_percent=0
    unbuffer irsync -v -K -r "${src}" "${dst}" | while read -r line; do
        w_done=$(( $w_done + 1 ))
        w_done_percent_new=$(( $w_done * 100 / $w_total ))
        if [ $w_done_percent_new -gt $w_done_percent ]; then
            w_done_percent=$w_done_percent_new
            echo $w_done_percent_new
        fi
    done
    exit ${PIPESTATUS[0]}
else
    echo "nothing to sync" 
    exit 0
fi
