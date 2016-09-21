#!/bin/bash

trap "cat /tmp/duck.err.$$ && rm -f /tmp/duck.*.$$ && kill -s SIGKILL -$$" SIGINT SIGKILL SIGTERM

function print_usage() {

    cat <<EOF
Usage:

  $ s-duck.sh <src> <dst>

  - src: source
  - dst: destination

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

# get username/password from the config file: $mydir/../config/default.json
rest_user=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['userName'])" )
rest_pass=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['userPass'])" )
dav_endpt=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['davEndpoint'])" )

src=$( echo $1 | sed 's/irods:/i:/g' )
dst=$( echo $2 | sed 's/irods:/i:/g' )

w_total=0

## check source type/existence
is_src_irods=0
is_src_dir=0
echo $src | egrep '^i:' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    is_src_irods=1
    src_coll=$( echo $src | sed 's/^i://' )

    t=$( ${mydir}/irodsGetNamespaceType.py --rest_user ${rest_user} --rest_pass ${rest_pass} ${src_coll} )
    if [ $? -ne 0 ]; then
        exit $?
    fi

    if [ "${t}" == "UNKNOWN" ]; then
        echo "file or collection not found: $src_coll" 1>&2
        exit 1
    elif [ "${t}" == "FILE" ]; then
        w_total=1
    else
        is_src_dir=1
        w_total=$( ${mydir}/irodsCountFilesInCollection.py --rest_user ${rest_user} --rest_pass ${rest_pass} ${src_coll} )
        if [ $? -ne 0 ]; then
            exit $?
        fi
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
is_dst_irods=0
is_dst_dir=0

echo $dst | egrep '^i:' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    is_dst_irods=1
    dst_coll=$( echo $dst | sed 's/^i://' )

    t=$( ${mydir}/irodsGetNamespaceType.py --rest_user ${rest_user} --rest_pass ${rest_pass} ${dst_coll} )

    if [ $? -ne 0 ]; then
        exit $?
    fi

    if [ "$t" == "UNKNOWN" ]; then
        is_dst_dir=$is_src_dir
    elif [ "$t" == "COLLECTION" ]; then
        is_dst_dir=1
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

if [ $is_src_irods -eq 1 ] && [ $is_dst_irods -eq 1 ] ; then
    echo "Not supported: both source and destination are iRODS endpoints" 1>&2
    exit 1
fi


# make sure the dst_dir is created
if [ $is_dst_dir -eq 1 ]; then
    if [ $is_dst_irods -eq 1 ]; then
        ${mydir}/irodsMakeDir.py --rest_user ${rest_user} --rest_pass ${rest_pass} "$( echo $dst | sed 's/^i://' )" > /dev/null 2>&1
    else
        mkdir -p "${dst}"
    fi
fi

# reconstruct the dst w/ proper filename
if [ $is_src_dir -eq 0 ] && [ $is_dst_dir -eq 1 ] ; then
    fname=$( echo $src | awk -F '/' '{print $NF}' )
    dst=${dst}/${fname}
fi

# run duck to sync data
if [ $w_total -gt 0 ]; then
    w_done=0
    w_done_percent=0

    dav_rootns=$( python -c "import json, os.path; c = json.load(open(os.path.join('${mydir}', '../config/default.json'))); print(c['RDM']['davRootNamespace'])" )

    if [ $is_dst_irods -eq 1 ]; then
        dst_coll=$(echo $dst | sed 's/^i://' | sed "s|${dav_rootns}||")
        duck_sync_url="$( echo ${dav_endpt} | sed 's/https/davs/' )${dst_coll}"
        duck_sync_dir=$src
        duck_sync_method="upload"
    else
        src_coll=$(echo $src | sed 's/^i://' | sed "s|${dav_rootns}||")
        duck_sync_url="$( echo ${dav_endpt} | sed 's/https/davs/' )${src_coll}"
        duck_sync_dir=$dst
        duck_sync_method="download"
    fi

    duck -y --parallel 2 -u ${rest_user} -p ${rest_pass} -e ${duck_sync_method} --synchronize \"${duck_sync_url}\" \"${duck_sync_dir}\" 2>/tmp/duck.err.$$ 1>/tmp/duck.out.$$ &
    duck_pid=$!

    p1=0
    while [ -d /proc/${duck_pid} ]; do

        sleep 1

        p2=$( tail /tmp/duck.out.$$ 2>/dev/null | grep -o -e '([0-9]\{1,3\}%,' | sed 's/(//' | sed 's/%,//' | tail -n 1 )

        if [ "$p2" != "" ]; then
            if [ $p2 -ne $p1 ]; then
                p1=$p2
                echo $p1
            fi
        fi
    done

    # wait to receive the exit code of the duck process 
    duck_ec=$(wait ${duck_pid})

    # make another check for the final progress after the duck process is gone
    p2=$( tail /tmp/duck.out.$$ 2>/dev/null | grep -o -e '([0-9]\{1,3\}%,' | sed 's/(//' | sed 's/%,//' | tail -n 1 )

    if [ "$p2" != "" ]; then
        if [ $p2 -ne $p1 ]; then
            p1=$p2
            echo $p1
        fi
    fi

    # too bad that duck doesn't return error when the sync is incomplete, we must check against the duck.out.$$
    tail /tmp/duck.out.$$ | grep -i 'Sync complete' > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        p1=100
        echo $p1
    else
        echo 'Sync incomplete' 1>&2
        duck_ec=1
        # print duck process's error
        if [ -f /tmp/duck.err.$$ ]; then
            cat /tmp/duck.err.$$ 1>&2
        fi
    fi

    # cleanup temporary files 
    rm -f /tmp/duck.*.$$ 2>/dev/null

    exit ${duck_ec}
else
    echo "nothing to sync" 
    exit 0
fi
