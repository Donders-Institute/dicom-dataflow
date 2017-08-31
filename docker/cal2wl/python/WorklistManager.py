#!/usr/bin/env python
from common.Logger import getLogger
from common.IMySQL import IMySQL
from common.Shell import Shell
from datetime import datetime, date, timedelta
from Cheetah.Template import Template
import ConfigParser
import sys
import os
import re
import getpass

class WorklistItem(object):

    def __init__(self, projectId, projectTitle, subjectId, sessionId, date, time, scanner, physician):
        self.projectId = projectId
        self.projectTitle = projectTitle
        self.subjectId = subjectId
        self.sessionId = 'ses-mri%s' % sessionId.zfill(2)
        self.sessionTitle = 'MR session %s' % sessionId.zfill(2)
        self.date = date
        self.time = time
        self.physician = physician
        self.eventId = '%s%s' % (self.date, self.time)   # evenId is taken as combination of date and time

        self.modalityAE = scanner

        if re.match('^[xX]',subjectId):  # subjectId with leading 'x' or 'X' is considered as an extra subject
            self.patientId = '%s_sub-x%s' % (projectId, re.sub('^[xX]','',subjectId).zfill(3))
        elif re.match('^Undefined',subjectId):  # undefined subject
            self.patientId = '%s_sub-%sT%s' % (projectId, date, time)
        else:
            self.patientId = '%s_sub-%s' % (projectId, subjectId.zfill(3))

        self.patientName = '%s_ses-%s' % (self.patientId, sessionId.zfill(2))

        self.studyId = '%s_S%s' % (projectId, sessionId.zfill(2))

    def getWorklistTemplate(self):
        """worklist template for Cheetah template engine"""

        worklist_tmpl ="""(0010,0010) PN  [$e['patientName']]
(0010,0020) LO  [$e['patientId']]
(0020,000d) UI  [$e['eventId']]
(0032,1032) PN  [$e['physician']]
(0008,0090) PN  [$e['physician']]
(0032,1060) LO  [$e['projectTitle']]
(0040,1001) SH  [$e['sessionId']]
(0040,0100) SQ
(fffe,e000) -
(0008,0060) CS  [MR]
(0040,0001) AE  [$e['modalityAE']]
(0040,0002) DA  [$e['date']]
(0040,0003) TM  [$e['time']]
(0040,0009) SH  [$e['sessionId']]
(0040,0010) SH  [$e['modalityAE']]
(0040,0011) SH  [DCCN]
(0040,0007) LO  [$e['sessionTitle']]
(0040,0008) SQ
(fffe,e0dd) - 
(fffe,e00d) -
(fffe,e0dd) -
"""

        return worklist_tmpl

    def __cmp__(self, other):
        """compare ModalityWorklist by date + time + patientId"""
        if not isinstance(other, WorklistItem):
            raise NotImplementedError
        return cmp(self.date, other.date) and cmp(self.time, other.time) and cmp(self.patientId, other.patientId)

    def __repr__(self):
        return str(Template(self.getWorklistTemplate(), searchList={'e': self.__dict__}))

class WorklistManager:

    def __init__(self, config):
        """
        class initializer
        :param config: configuration file for WorklistManager 
        :return:
        """

        cfg_defaults = {'pdb_hostname': 'localhost',
                        'pdb_username': 'test',
                        'pdb_password': 'guessit',
                        'pdb_dbname': 'fcdctest',
                        'mr_scanner_regex': '.*(SKYRA|PRASMA(FIT)).*',
                        'dcmtk_setup_cmd': '',
                        'dcmtk_wlbroker_store': '/scratch/OrthancData/DicomWorklist/WLBROKER'}

        cfg = ConfigParser.ConfigParser(defaults=cfg_defaults)
        cfg.read(config)

        self.mr_scanner_regex = re.compile(cfg.get('WLBROKER','mr_scanner_regex'))
        self.dcmtk_setup = cfg.get('WLBROKER','dcmtk_setup_cmd')
        self.dcmtk_wlbroker_dir = cfg.get('WLBROKER','dcmtk_wlbroker_store')
        self.logger = getLogger(name=self.__class__.__name__, lvl=int(cfg.get('LOGGING', 'level')))

        self.__getDBConnectInfo__(cfg)
        self.pdb = IMySQL(db_host = self.pdb_host,
                          db_username = self.pdb_uid,
                          db_password = self.pdb_pass,
                          db_name = self.pdb_name)

    def __del__(self):
        self.pdb.closeConnector()

    def __getDBConnectInfo__(self, cfg):
        '''common function to get database connection information
        '''
        ## project database connection information
        self.pdb_host   = cfg.get('PDB','pdb_hostname')
        self.pdb_uid    = cfg.get('PDB','pdb_username')
        self.pdb_pass   = cfg.get('PDB','pdb_password')
        self.pdb_name   = cfg.get('PDB','pdb_dbname')
 
        if not self.pdb_pass:
            ## try ask for password from the interactive shell
            if sys.stdin.isatty(): ## for interactive password typing
                self.pdb_pass = getpass.getpass('Project DB password: ')
            else: ## for pipeing-in password
                print 'Project DB password: '
                self.pdb_pass = sys.stdin.readline().rstrip()

    def makeDicomWorklist(self, eDate=date.today(), worklistStore=''):
        """
        make worklist items for DICOM worklist broker
        :param eDate: the date in which the MR scan is planned
        :param worklistStore: (optional) the filesystem path in which the DICOM worklist items will be stored.
                              If it's specified, it replaces the path specified by 'dcmtk_wlbroker_store' in
                              the config file.
        :return: a list of filesystem paths to the successfully created worklist items
        """

        worklistFiles = []

        s = Shell()
        dump2dcm_cmd = 'dump2dcm'
        if self.dcmtk_setup:
            dump2dcm_cmd = '%s; %s' % (self.dcmtk_setup, dump2dcm_cmd)

        if not worklistStore:
            worklistStore = self.dcmtk_wlbroker_dir

        for wl in self.getWorklistItems(eDate):
            # save worklist as human-readable (DICOM dump)
            dump_fpath = os.path.join(worklistStore, '%s_%s.dump' % (wl.modalityAE, wl.eventId))
            f = open( dump_fpath,'w')
            f.write( str(wl) )
            f.close()

            # convert DICOM dump to DICOM format
            dcm_fpath = os.path.join(worklistStore, '%s_%s.wl' % (wl.modalityAE, wl.eventId))
            s_cmd = '%s %s %s' % (dump2dcm_cmd, dump_fpath, dcm_fpath)
            self.logger.debug('dump2dcm command: %s' % s_cmd)
            rc,output,m = s.cmd1(s_cmd)
            if rc != 0:
                self.logger.error('DICOM worklist item creation failed: ' % wl.studyId)
            else:
                worklistFiles.append(dcm_fpath)

        return worklistFiles

    def getWorklistItems(self, eDate=date.today()):
        '''compose worklist items based on booking events retrieved from calendar table in PDB
        '''

        conn = self.pdb.getConnector()
        crs  = None

        worklist = []

        try:
            qry = 'SELECT a.id,a.project_id,a.subj_ses,a.start_date,a.start_time,a.user_id,b.projectName,c.description AS lab_desc FROM calendar_items_new AS a, projects AS b, calendars AS c WHERE a.status IN (\'CONFIRMED\',\'TENTATIVE\') AND a.subj_ses NOT IN (\'Cancellation\',\'0\') AND a.start_date = DATE(\'%s\') AND a.project_id = b.id AND a.calendar_id = c.id ORDER BY a.start_time' % eDate.strftime('%Y-%m-%d')

            self.logger.debug(qry)

            crs = conn.cursor()
            crs.execute(qry)

            for (eId, projectId, subj_ses, startDate, startTime, userId, projectName, labDesc) in crs.fetchall():

                # only events for MR scanners are considered
                m = self.mr_scanner_regex.match(labDesc.upper())

                if not m:
                    continue

                scannerAE = m.group(1)

                d = re.compile('\s*(-)\s*').split(subj_ses)
                subjectId = d[0]

                # always set session id to '1' if it's not part of subj_ses string 
                sessionId = d[-1] if len(d) > 1 else '1'

                # in some MySQL library, the startTime is returned as timedelta object
                eStartTime = None
                if type(startTime) is timedelta:
                    eStartTime = datetime(startDate.year, startDate.month, startDate.day)
                    eStartTime += startTime
                else:
                    eStartTime = startTime

                # make another SQL query to get user name
                try:
                    crs1 = conn.cursor()
                    crs1.execute('SELECT firstName,lastName FROM users WHERE id = \'%s\'' % userId)
                    (firstName, lastName) = crs1.fetchone()
                    userId = '%s %s' % (firstName, lastName)
                except Exception, e:
                    self.logger.exception('User name select failed: %s' % userId)
                else:
                    pass
                finally:
                    try:
                        crs1.close()
                    except Exception, e:
                        pass

                # construct worklist item
                wl = WorklistItem(projectId,
                                  projectName,
                                  subjectId,
                                  sessionId,
                                  startDate.strftime('%Y%m%d'),
                                  eStartTime.strftime('%H%M%S'),
                                  scannerAE,
                                  userId)

                worklist.append(wl)

        except Exception, e:
            self.logger.exception('Project DB select failed')
        else:
            ## everything is fine
            self.logger.info('Project DB select succeeded')
        finally:
            ## close db cursor
            try:
                crs.close()
            except Exception, e:
                pass

            self.pdb.closeConnector()

        return worklist
