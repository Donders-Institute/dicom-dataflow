#!/usr/bin/env python
import argparse
import os
import sys

sys.path.append('%s/external' % os.environ['PYTHON_LIBDIR'])
sys.path.append('%s/donders' % os.environ['PYTHON_LIBDIR'])

from rdm.IRDM import IRDMRestful

from common.Logger import getLogger

if __name__ == "__main__":

    # command-line argument validators
    def valid_path(s):
        if os.path.isfile(s):
            return s
        else:
            msg = "Invalid filesystem path: %s" % s
            raise argparse.ArgumentTypeError(msg)

    parg = argparse.ArgumentParser(description='get the next valid HOTP of the given iRODS username')

    parg.add_argument('username',
                      metavar = 'username',
                      type = str,
                      help = 'specify the iRODS username')

    ## optional arguments
    parg.add_argument('--config',
                      action='store',
                      dest='config',
                      type=valid_path,
                      default='%s/../config/config.ini' % os.path.dirname(os.path.realpath(__file__)),
                      help='specify the configuration file for connecting the DI-RDM services')

    parg.add_argument('--rest_user',
                      action='store',
                      dest='rest_user',
                      type=str,
                      default='irods',
                      help='specify the name of the user by whom the HOTP request is to made, usually it is user "irods"')

    parg.add_argument('--rest_pass',
                      action='store',
                      dest='rest_pass',
                      type=str,
                      default='xxxx',
                      help='specify the password of the user by whom the HOTP request is to made, usually it is the one-time password')


    args = parg.parse_args()
    logger = getLogger(name=os.path.basename(__file__), lvl=3)

    irdm = IRDMRestful(args.config, lvl=3)
    irdm.irods_username = args.rest_user 
    irdm.irods_password = args.rest_pass
    rule_fpath = os.path.join(os.path.join(os.environ['PYTHON_LIBDIR'], './donders/rdm/rules', 'getUserNextHOTP.r'))

    out = irdm.__rdm_exec_rule__(irule_script=rule_fpath, inputs={'userName': args.username})

    # print HOTP or error message
    if out['ec'] == 0:
        print(out['otp'])
    else:
        logger.error(out['errmsg'])

    # return exit code
    sys.exit( out['ec'] )
