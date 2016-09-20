#!/usr/bin/env python
import argparse
import os
import sys
import json
import ConfigParser

sys.path.append('%s/external' % os.environ['PYTHON_LIBDIR'])
sys.path.append('%s/donders' % os.environ['PYTHON_LIBDIR'])
from common.Logger import getLogger

if __name__ == "__main__":

    parg = argparse.ArgumentParser(description='generate RDM configuration files from the config/default.json')

    ## optional arguments
    parg.add_argument('--rdm_config',
                      action='store',
                      dest='p_rdm_config',
                      type=str,
                      default='%s/../config/config.ini' % os.path.dirname(os.path.realpath(__file__)),
                      help='specify the configuration file for connecting the DI-RDM services, used for RDM WebDAV and RESTful interfaces')

    parg.add_argument('--irods_environment',
                      action='store',
                      dest='p_irods_environment',
                      type=str,
                      default='%s/.irods/irods_environment.json' % os.environ['HOME'],
                      help='specify the location of irods_environment.json file, used for iCommands')

    args = parg.parse_args()
    logger = getLogger(name=os.path.basename(__file__), lvl=3)

    config = '%s/config/default.json' % os.path.dirname(os.path.realpath(__file__))


    if not os.path.exists(config):
        raise IOError('file not found: %s' % config)

    f = open(config, 'r')
    c = json.load(f)
    f.close()

    # update irods_environment.json file 
    c_irods_env = {} 
    if os.path.exists(args.p_irods_environment):
        f = open(args.p_irods_environment, 'r')
        c_irods_env = json.load(f)
        f.close()

    c_irods_env['irods_user_name'] = c['RDM']['userName']
    c_irods_env['irods_host'] = c['RDM']['icatHost']
    c_irods_env['irods_port'] = c['RDM']['icatPort']

    f = open(args.p_irods_environment, 'w')
    json.dump(c_irods_env, f, indent=4, sort_keys=True)
    f.close()

    # update config.ini file
    c_rdm = ConfigParser.ConfigParser()
    if os.path.exists(args.p_rdm_config):
        c_rdm.read(args.p_rdm_config)

    if not c_rdm.has_section('RDM'):
        c_rdm.add_section('RDM')

    if not c_rdm.has_section('LOGGING'):
        c_rdm.add_section('LOGGING')

    c_rdm.set('RDM', 'irods_rest_endpt', c['RDM']['restEndpoint'])
    c_rdm.set('RDM', 'irodsUserName', c['RDM']['userName'])
    c_rdm.set('RDM', 'irodsPassword', '')
    c_rdm.set('LOGGING', 'level', '0')

    f = open(args.p_rdm_config, 'wb')
    c_rdm.write(f)
    f.close()
