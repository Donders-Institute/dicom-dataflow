#!/bin/bash

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

export PATH=$PYTHON_BINDIR:$PATH

# generate necessary configuration files for interfacing RDM services
cwd=$( get_script_dir $0 )
${cwd}/config_stager.py --rdm_config ${cwd}/config/config.ini --irods_environment ${IRODS_ENVIRONMENT_FILE} 

if [ $? -ne 0 ]; then
    echo "fail generating stager config files" 1>&2
    exit 1
fi

# initialise iRODS authN token for iCommands
python -c 'import json; c = json.load(open("config/default.json")); print(c["RDM"]["userPass"])' | iinit

$NODEJS_PREFIX/bin/node stager.js
