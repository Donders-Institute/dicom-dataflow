#!/usr/bin/env python
import hashlib
import json
from datetime import datetime
from zipfile import ZipFile
import ConfigParser

from common.Logger import getLogger
from common.IRESTful import IRESTful, SimpleCallback, FileIOCallback

class OrthancDicomMetadata(object):
    """
    generic data object of OrthancDicomMetadata
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __cmp__(self, other):
        """compare OrthancDicomMetadata by ID"""
        if not isinstance(other, OrthancDicomMetadata):
            raise NotImplementedError
        return cmp(self.ID, other.ID)

    def __repr__(self):
        return repr(self.__dict__)

def decoder_OrthancDicomMetadata(obj):
    """
    json object decoder for generic OrthancDicomMetadata
    :param obj: the dict json structure from json.loads
    :return: the generic OrthancDicomMetadata
    """
    return OrthancDicomMetadata(**obj)

class IOrthanc:
    """
    class for Orthanc client interface using IRESTful pyCURL wrapper
    """

    def __init__(self, config):
        """
        class initializer
        :param config: configuration file for Orthanc server connection
        :return:
        """

        cfg = ConfigParser.ConfigParser()
        cfg.read(config)
        self.logger = getLogger(name=self.__class__.__name__, lvl=int(cfg.get('LOGGING', 'level')))

        self.host = cfg.get('PACS','orthanc_host')
        self.port = cfg.get('PACS','orthanc_port')

    def getArchive(self, rsrc_path, dest_fpath, progress=False, checksum=True):
        """
        downloads DICOM archive zip file for a given collective resource such as
        patient, study, series
        :param rsrc_path: the RESTful resource path
        :param dest_fpath: the path to the destination zip file
        :param progress: turn on progress indication if set to True
        :param checksum: calculate checksum value of each entry of the zip archive
        :return: True if success, otherwise False
        """
        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.accept = 'application/zip'
        rest.resource = '%s/archive' % rsrc_path
        cb = FileIOCallback("download", dest_fpath, progress)
        ick = rest.doGET(cb)

        if not ick:
            self.logger.error('failed to download archive')
        
        cb.close()

        if checksum:
            checksums = {}

            # calculate checksum for every entries in the zip file
            fzip = ZipFile(file=dest_fpath, mode='r', allowZip64=True)
            blocksize = 65563
            for n in fzip.namelist():
                hasher = hashlib.md5()
                f = fzip.open(n, 'r')
                buf = f.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(blocksize)
                f.close()

                # compose checksum data for entries within each top-level (i.e. study) directory
                fpath_data = n.split('/')
                topdir = fpath_data[0]
                arcname = '/'.join(fpath_data[1:])

                try:
                    checksums[topdir] += '%s %s\n' % (arcname, hasher.hexdigest())
                except KeyError, e:
                    checksums[topdir] = '%s %s\n' % (arcname, hasher.hexdigest())

            fzip.close()

            # save the checksum of entries back the zip file
            fzip = ZipFile(file=dest_fpath, mode='a', allowZip64=True)
            # open md5sum.txt within each study directory to store the calculated checksum
            for k,v in checksums.iteritems():
                fzip.writestr(zinfo_or_arcname='%s/md5sum.txt' % k, bytes=v)
            fzip.close()

        return ick

    def getStudies(self, last_update_range, stableOnly=False):
        """
        gets list of Study data objects with last update in certain time range
        :param last_update_range: the 2-element tuple containing datetime objects corresponding to the lower and the upper boundaries
        :param stableOnly: set True to get only stable studies
        :return: a list of OrthancDicomMetadata objects of "Study" type
        """

        studies = []

        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = 'studies'
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if not ick:
            self.logger.error('failed to get list of studies')
        else:
            for s in json.loads(cb.contents):
                self.logger.debug('retrieve study: %s' % s)
                s_obj = self.__getStudyMetadata__('studies/%s' % s)
                if not s_obj:
                    self.logger.error('failed to get study metadata: %s' % s)
                else:
                    t_update = datetime.strptime(s_obj.LastUpdate, '%Y%m%dT%H%M%S')
                    if last_update_range[0] <= t_update < last_update_range[1]:
                        studies.append(s_obj)

        if stableOnly:
            return filter(lambda x:x.IsStable, studies)
        else:
            return studies

    def getChanges(self, since, limit):
        """
        gets Orthanc changes
        :param since: change sequence id from which the changes are retrieved
        :param limit: number of changes to be retrieved
        :return: (end-of-change flag, a list of retrieved Changes)
        """

        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = 'changes'
        rest.params = ['since=%d' % since, 'limit=%d' % limit]
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            data = json.loads(cb.contents, object_hook=decoder_OrthancDicomMetadata)
            return data.Done, data.Changes
        else:
            return None

    def __getInstanceMetadata__(self, rsrc_path):
        """
        gets instance metadata from the given resource path
        :param rsrc_path: the resource path to the instance
        :return: the OrthancDicomMetadata object of "Instance" type
        """
        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = rsrc_path
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            return json.loads(cb.contents, object_hook=decoder_OrthancDicomMetadata)
        else:
            return None

    def __getSeriesMetadata__(self, rsrc_path):
        """
        gets series metadata from the given resource path
        :param rsrc_path: the resource path to the series
        :return: the OrthancDicomMetadata object of "Series" type
        """
        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = rsrc_path
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            return json.loads(cb.contents, object_hook=decoder_OrthancDicomMetadata)
        else:
            return None

    def __getStudyMetadata__(self, rsrc_path):
        """
        gets study metadata from the given resource path
        :param rsrc_path: the resource path to the study
        :return: the OrthancDicomMetadata object of "Study" type
        """
        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = rsrc_path
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            return json.loads(cb.contents, object_hook=decoder_OrthancDicomMetadata)
        else:
            return None

    def __getPatientMetadata__(self, rsrc_path):
        """
        gets patient metadata from the given resource path
        :param rsrc_path: the resource path to the patient
        :return: the OrthancDicomMetadata object of "Patient" type
        """
        rest = IRESTful('http://%s:%s' % (self.host, str(self.port)))
        rest.resource = rsrc_path
        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            return json.loads(cb.contents, object_hook=decoder_OrthancDicomMetadata)
        else:
            return None
