#!/usr/bin/env python

import os
import sys
import argparse
from datetime import date, datetime, timedelta
sys.path.append('%s/external' % os.environ['DCCN_PYTHONDIR'])
sys.path.append('%s/lib' % os.environ['DCCN_PYTHONDIR'])
from orthanc.WorklistManager import WorklistManager

# execute the main program
if __name__ == "__main__":

    # command-line argument validators
    def valid_path(s):
        if os.path.isfile(s):
            return s
        else:
            msg = "Invalid filesystem path: %s" % s
            raise argparse.ArgumentTypeError(msg)

    def valid_dir(s):
        if os.path.isdir(s):
            return s
        else:
            msg = "Invalid filesystem directory: %s" % s
            raise argparse.ArgumentTypeError(msg)

    def valid_date(s):
        if not s:
            return date.today()
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    # command-line argument parser
    p = argparse.ArgumentParser(description='convert MR lab-booking events into DICOM worklist', version="0.1")

    # optional arguments
    p.add_argument('-c','--config',
                    action  = 'store',
                    dest    = 'config',
                    type    = valid_path,
                    default = '%s/config/config.ini' % os.environ['DCCN_PYTHONDIR'],
                    help    = 'specify the configuration file')

    p.add_argument('-d', '--date',
                    dest    = 'date',
                    action  = 'store',
                    type    = valid_date,
                    default = date.today().strftime('%Y-%m-%d'),
                    help    = 'date in %%Y-%%m-%%d format, e.g. 2016-01-01')

    p.add_argument('-s', '--store',
          dest    = 'wl_dir',
          action  = 'store',
          type    = valid_dir,
          default = '/tmp',
          help    = 'specify the path in which the DICOM worklist are created')

    p.add_argument('--dryrun',
                   dest    = 'dryrun',
                   action  = 'store_true',
                   default = False,
                   help    = 'print the DICOM dump instead of actually creating the worklist to the broker')

    args = p.parse_args()

    # worklist manager
    wlmgr = WorklistManager(config=args.config)

    print('worklist items for date: %s' % args.date)
    if args.dryrun:
        for wl in wlmgr.getWorklistItems(eDate = args.date):
            print('%s' % wl)
    else:
        for wl in wlmgr.makeDicomWorklist(eDate = args.date, worklistStore=args.wl_dir):
            print('%s' % wl)