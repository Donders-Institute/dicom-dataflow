#!/usr/bin/env python
import ConfigParser
import json
import os
import re
import pexpect
from datetime import datetime
from sets import Set
from tempfile import NamedTemporaryFile
from common.Logger import getLogger
from common.IRESTful import IRESTful, SimpleCallback, FileIOCallback
from common.Shell import Shell
from common.Utils import inputPassword, sizeof_fmt

class IRDMException(Exception):
    """
    RDM interface general exception
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ICommandError(IRDMException):
    """
    Exception raised when icommands execution failed.
    """

    def __init__(self, cmd, ec, out):
        self.cmd = cmd
        self.ec = ec
        self.out = out
        self.msg = '"%s" failed with exit code: %d\n' % (self.cmd, self.ec)

class IrodsFile:
    """
    data object of iRODS file (more precisely the iRODS data object)
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __cmp__(self, other):
        """compare IrodsFile by path"""
        if not isinstance(other, IrodsFile):
            raise NotImplementedError
        return cmp(os.path.join(self.COLL_NAME, self.DATA_NAME), os.path.join(other.COLL_NAME, other.DATA_NAME))

    def __hash__(self):
        return hash(os.path.join(self.COLL_NAME, self.DATA_NAME))

    def __repr__(self):

        _ftype = ''
        if self.TYPE == 'COLLECTION':
            _ftype = 'D'

        return '{!s:19} {!s:>8} {:1} {}'.format(datetime.fromtimestamp(self.MODIFY_TIME / 1000), sizeof_fmt(self.SIZE), _ftype, self.PATH)

class IRDM:
    """
    super class defining the IRDM interface without actual implementation
    """
    def __init__(self, config, lvl=0):
        self.IF_TYPE = None
        self.lvl = lvl

        default_cfg = {
            'irods_rest_endpt': 'http://rdmapptst.uci.ru.nl:8080/irods-rest-4.0.2.1-SNAPSHOT/rest',
            'irods_admin_username': 'irods',
            'irods_admin_password': '',
            'irods_admin_authfile': os.path.join(os.path.expanduser('~'), '.irods/irdm/.irodsA_rdm_admin'),
            'irodsAuthCached': 'true',
            'irodsAuthFileName': os.path.join(os.path.expanduser('~'), '.irods/irdm/.irodsA'),
            'irodsSSLCACertificateFile': os.path.dirname(os.path.abspath(__file__)) + '/../ssl/irods-icat_chain.pem'
        }
        self.config = ConfigParser.SafeConfigParser(default_cfg)

        if config and os.path.exists(config):
            self.config.read(config)

        # try to overwrite the logging level with the specification in the config file
        try:
            self.lvl = int(self.config.get('LOGGING','level'))
        except:
            pass

        self.logger = getLogger(name=self.__class__.__name__, lvl=self.lvl)

        self.is_user_login = False

    def login(self):
        """
        logs into RDM service.
        The implementation should probe the user authentication and switch self.is_user_login accordingly.
        :return:
        """
        self.is_user_login = True

    def logout(self):
        """
        logs out from the RDM service.
        The implementation should logout the service (e.g. clean up authentication tokens.
        :return:
        """
        self.is_user_login = False

    def mkdir(self, ns_collection, rel_path):
        """
        makes directory (or collection in iRODS terminology) and non-existing parent directories (collections)
        within a RDM collection namespace.
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path
        :return: True if success; otherwise raises IRDMException
        """
        raise NotImplementedError

    def irods_mkdir(self, irods_path):
        """
        makes directory (or collection in iRODS terminology) and non-existing parent directories (collections).
        :param irods_path: the iRODS path
        :return: True if success; otherwise raises IRDMException
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.mkdir(ns_collection, rel_path)

    def rmdir(self, ns_collection, rel_path, force=False):
        """
        removes a folder within a RDM collection namespace.
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path to the folder
        :param force: True for removing child files and folders
        :return: True if success; otherwise raises IRDMException
        """
        raise NotImplementedError

    def irods_rmdir(self, irods_path, force=False):
        """
        removes a irods directory
        :param irods_path: the iRODS path
        :param force: True for removing child files and folders
        :return: True if success; otherwise raises IRDMException
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.rmdir(ns_collection, rel_path, force=force)

    def rm(self, ns_collection, rel_path, force=False):
        """
        removes a file within a RDM collection namespace
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path to the file
        :param force: remove the file forcefully
        :return: True if success; otherwise raises IRDMException
        """
        raise NotImplementedError

    def irods_rm(self, irods_path, force=False):
        """
        removes a iRODS file
        :param irods_path: the iRODS path
        :param force: remove the file forcefully
        :return: True if success; otherwise raises IRDMException
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.rm(ns_collection, rel_path, force=force)

    def get(self, ns_collection, rel_path, dest_path, show_progress=False):
        """
        downloads a file within a RDM collection namespace, to a path on the local filesystem.
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path to the file or the folder
        :param dest_path: the destination path on the local filesystem
        :param show_progress: True for showing file transfer progress
        :return: True if success; otherwise raises IRDMException
        """
        raise NotImplementedError

    def irods_get(self, irods_path, dest_path, show_progress=False):
        """
        downloads a iRODS file or contents in a iRODS directory
        :param irods_path: the iRODS path
        :param dest_path: the destination path on the local filesystem
        :param show_progress: True for showing file transfer progress
        :return: True if success; otherwise raises IRDMException
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.get(ns_collection, rel_path, dest_path, show_progress=show_progress)

    def put(self, src_path, ns_collection, rel_path, show_progress=False):
        """
        uploads a file on the local filesystem, into a RDM collection namespace.
        :param src_path: the source path on the local filesystem
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path to a target file or folder within the RDM collection
        :param show_progress: True for showing file transfer progress
        :return: True if success; otherwise raises IRDMException
        """
        raise NotImplementedError

    def irods_put(self, src_path, irods_path, show_progress=False):
        """
        uploads a file or contents in a folder on the local filesystem to iRODS
        :param src_path: the source path on the local filesystem
        :param irods_path: the iRODS path
        :param show_progress: True for showing file transfer progress
        :return: True if success; otherwise raises IRDMException
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.put(src_path, ns_collection, rel_path, show_progress=show_progress)

    def ls(self, ns_collection, rel_path, recursive=False):
        """
        lists files in a directory within a RDM collection namespace.
        :param ns_collection: the RDM collection namespace
        :param rel_path: the relative path
        :param recursive: True if looping over sub-directories
        :return: list of files/folders with preliminary system metadata; or raises IRDMException when failed
        """
        raise NotImplementedError

    def irods_ls(self, irods_path, recursive=False):
        """
        lists files in a directory within a iRODS directory
        :param irods_path: the iRODS path
        :param recursive: True if looping over sub-directories
        :return:list of files/folders with preliminary system metadata; or raises IRDMException when failed
        """
        (ns_collection, rel_path) = self.__get_collection_datapath__(irods_path)
        return self.ls(ns_collection, rel_path, recursive=recursive)

    def adminSetUserCollectionRole(self, irods_userid, ns_collection, role):
        """
        sets given irods user to a role of a collection.
        NB: the user is removed from other role of the collection if it presents.
        :param irods_userid: the irods user id
        :param ns_collection: the RDM collection namespace
        :param role: one of the predefined roles: manager, reviewer, contributor, viewer;
                     or 'null' to remove user's role in the collection
        :return: True on success
        """
        raise NotImplementedError

    def adminGetUserCollectionRole(self, irods_userid, ns_collection):
        """
        gets given irods user's role of a collection.
        :param irods_userid: the irods user id
        :param ns_collection: the RDM collection namespace
        :return: the user's role in the collection; None if user doesn't have a role in the collection
        """
        return self.adminGetUserRolesInScope(irods_userid, ns_collection)

    def adminGetUserRoles(self, irods_userid):
        """
        gets RDM roles of a given irods user id.
        :param irods_userid: the user id
        :return: a dictionary with scope (organisation, organisation unit, collection namespace) as key,
                 and user roles as value.
        """
        raise NotImplementedError

    def adminGetUserRolesInScope(self, irods_userid, scope):
        """
        gets user's role in an RDM scope
        :param irods_userid: the user id
        :param scope: the RDM scope (organisation, organisation unit, collection namespace)
        :return: a dictionary with scope name as key, and user roles as value.
        """
        raise NotImplementedError

    def adminGetUsersInScope(self, scope):
        """
        gets all users has access to the given RDM scope.
        :param scope: the RDM scope referring to an organisation, organisation unit or a collection namespace
        :return: a dictionary with role as key, and members as value
        """

        users = {}
        for g in self.__rdm_get_roles_as_groups__(scope):
            users[self.__rdm_get_role_function__(g)] = self.__irods_group_get_members__(g)

        return users

    def __irods_collection_get_id_from_ns__(self, ns_collection):
        """
        gets the internal irods collection id given the RDM collection namespace
        :param ns_collection: the RDM collection namespace
        :return: the irods collection id
        """
        raise NotImplementedError

    def __irods_collection_get_ns_from_id__(self, id_collection):
        """
        gets the RDM collection namespace given the irods collection id
        :param id_collection: the collection id
        :return: the RDM collection namespace
        """
        raise NotImplementedError

    def __irods_user_exists__(self, irods_userid):
        """
        checks if the given user is presented in iRODS
        :param irods_userid: the user id
        :return: True if exists; otherwise False
        """
        raise NotImplementedError

    def __irods_user_get_memberships__(self, irods_userid):
        """
        gets group memberships of the given irods user id.
        :param irods_userid: the irods user id
        :return: a list of user's group memberships
        """
        raise NotImplementedError

    def __irods_group_get_members__(self, irods_group):
        """
        gets users in a irods group
        :param irods_group: the irods group name
        :return: a list of users
        """
        raise NotImplementedError

    def __irods_group_add_member__(self, irods_group, irods_userid):
        """
        adds user to an irods group.
        :param irods_group: the irods group
        :param irods_userid: the irods user id
        :return:
        """
        raise NotImplementedError

    def __irods_group_remove_member__(self, irods_group, irods_userid):
        """
        removes user from an irods group.
        :param irods_group: the irods group
        :param irods_userid: the irods user id
        :return:
        """
        raise NotImplementedError

    def __rdm_collection_get_ou_from_ns__(self, ns_collection):
        """
        gets organisation unit name from the given RDM collection namespace
        :param ns_collection: the RDM collection namespace
        :return: the organisation unit name
        """
        return str.rstrip(ns_collection, '/').split('/')[-2]

    def __rdm_get_roles_as_groups__(self, scope):
        """
        gets roles of the given RDM scope (organisation, organisation unit, collection namespace)
        in terms of irods groups.
        :param scope: the RDM scope
        :return: a list of irods groups
        """
        return NotImplementedError

    def __rdm_resolve_scope__(self, scope):
        """
        resolves the scope into internal scope string used as prefix of iRODS group
        :param scope: the name of the scope referring to organisation, organisation or collection namespace
        :return: the internal scope string
        """

        myscope = scope

        # the scope defined by a collection namespace, convert the namespace to collection id
        if re.match('^/.*', myscope):
            # get id of ns_collection
            id_coll = self.__irods_collection_get_id_from_ns__(myscope)

            if not id_coll:
                raise IRDMException('scope not found: %s' % scope)
            else:
                myscope = id_coll

        return myscope

    def __rdm_get_role_scope__(self, irods_group):
        """
        gets the scope of the RDM role referred by a iRODS group name.
        :param irods_group: the iRODS group name
        :return:
        """
        return '_'.join(irods_group.split('_')[:-1])

    def __rdm_get_role_function__(self, irods_group):
        """
        gets the function of the RDM role referred by a iRODS group name.
        :param irods_group: the iRODS group name
        :return:
        """
        return irods_group.split('_')[-1]

    def __get_collection_datapath__(self, ns_irods):
        """
        splits the iRODS namespace into two parts:
          1. the iRODS namespace to the RDM collection
          2. the relative datapath within the collection

        NOTE: this function is based on the following namespace convention:

        /rdmtst/di/centre_name/collection_name/data/in/collection

        in the example above, the ns_collection is '/rdmtst/di/centre_name/collection_name',
        and the rel_path is 'data/in/collection'

        :param ns_irods: the iRODS namespace
        :return: a tuple containing (ns_collection, rel_path)
        """

        # TODO: the hardcoded path should be improved
        re_ns_centre = re.compile('^(/rdmtst/di/(dccn|dcc|dcn))')

        m = re_ns_centre.match(ns_irods)

        if m:
            ns_centre = m.group(1)
            _parts = re.sub('%s/' % ns_centre, '', ns_irods).split('/')
            ns_collection = '%s/%s' % (ns_centre, _parts[0])
            rel_path = '/'.join(_parts[1:])
            return ns_collection, rel_path
        else:
            return '', ns_irods

    def __rdm_exec_rule__(self, irule_script, inputs, output="*out", outfmt='json', admin=False):
        """
        executes the given irule script
        :param irule_script: the file path to the irule script 
        :param inputs: a JSON document containing input arguments for the irule script
                       The format of it is:

                       {"param1" : "value1", "param2" : "value2"}

                       It will be converted into the following equivalent irule command:

                       $ irule -F <irule_script> *param1='"value1"' *param2='"value2"'  

        :param output: the output parameter of the rule, default is *out 
        :param outfmt: the output parameter format, default is json 
        :return: a dictionary loaded from a returned JSON document
                 strings in the dictionary are utf-8 encoded.
        """
        raise NotImplementedError

class IRDMRestful(IRDM):
    """
    RDM interface implementation using RESTful interface
    """

    def __init__(self, config, lvl=0):
        """
        initalizer with configuration file.
        """
        IRDM.__init__(self, config, lvl=lvl)
        self.IF_TYPE = 'RESTful'
        self.irods_username = self.config.get('RDM', 'irodsUserName')
        self.irods_password = self.config.get('RDM', 'irodsPassword')

        try:
            self.irods_rest_servercert = self.config.get('RDM','irods_rest_servercert')
        except:
            self.irods_rest_servercert = ''

    def login(self):
        """
        perform a simple IRESTful ping with given user credential.  On success, set self.is_user_login to True
        :return:
        """
        # ask password from stdin if it's unavailable
        if not self.irods_password:
            self.irods_password = inputPassword('iRODS %s password (%s)' % (self.irods_username, self.config.get('RDM','irodsAuthScheme')))

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'server'
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if ick:
            self.is_user_login = True
        else:
            raise IRDMException('fail to ping server: %s' % rest.resource)

    def logout(self):
        # remove cached password for irods account.
        self.irods_password = None
        self.is_user_login = False

    def ls(self, ns_collection, rel_path, recursive=False):

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'collection/%s/%s' % (ns_collection, rel_path)
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        self.logger.debug('listing resource: %s' % rest.resource)

        rest.params.append('listType=both')
        rest.params.append('listing=True')

        cb = SimpleCallback()
        ick = rest.doGET(cb)

        irods_files = []

        if ick:

            children = []
            try:
                children = self.__collection_children_list__(json.loads(cb.contents)['children'])
            except KeyError, e:
                pass

            for c in children:

                f ={}
                f['TYPE'] = c['objectType']
                f['PATH'] = os.path.join(c['parentPath'], c['pathOrName'])
                f['OWNER'] = '%s@%s' % (c['ownerName'], c['ownerZone'])
                f['SIZE'] = c['dataSize']
                f['CREATE_TIME'] = c['createdAt']
                f['MODIFY_TIME'] = c['modifiedAt']

                # TODO: for DATA_OBJECT type, more information such as checksum, number of replicas
                #       should be checked by using another RESTful call as the example below:
                #
                #       -----
                #       rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
                #       rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
                #       rest.resource = 'dataObject/%s/%s' % (c['parentPath'], c['pathOrName'])
                #       cb = SimpleCallback()
                #       ick1 = rest.doGET(cb)
                #       if ick1:
                #           d = json.loads(cb.contents)['irods-rest.dataObject']
                #           f['DATA_CHECKSUM'] = d['checksum']
                #       -----
                #
                irods_files.append(IrodsFile(**f))

                if c['objectType'] == 'COLLECTION' and recursive:
                        irods_files += self.ls(c['pathOrName'], '', recursive)

        return irods_files

    def mkdir(self, ns_collection, rel_path):

        paths = rel_path.split('/')

        for i in xrange(len(paths)):
            i += 1
            rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
            rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
            rest.resource = 'collection/%s/%s' % (ns_collection, '/'.join(paths[0:i]))
            rest.cainfo = self.irods_rest_servercert
            if not rest.cainfo:
                rest.ignore_ssl_cert_check = True

            self.logger.debug('creating resource: %s' % rest.resource)

            cb = SimpleCallback()
            ick = rest.doPUT(cb)

            if not ick:
                raise IRDMException('cannot create resource: %s' % rest.resource)

        return True

    def rmdir(self, ns_collection, rel_path, force=False):

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'collection/%s/%s' % (ns_collection, rel_path)
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        self.logger.debug('removing resource: %s' % rest.resource)

        if force:
            rest.params.append('force=True')

        cb = SimpleCallback()
        ick = rest.doDELETE(cb)

        if not ick:
            raise IRDMException('cannot remove resource: %s' % rest.resource)

        return True

    def rm(self, ns_collection, rel_path, force=False):

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'dataObject/%s/%s' % (ns_collection, rel_path)
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        self.logger.debug('removing resource: %s' % rest.resource)

        if force:
            rest.params.append('force=True')

        cb = SimpleCallback()
        ick = rest.doDELETE(cb)

        if not ick:
            raise IRDMException('cannot remove resource: %s' % rest.resource)

    def get(self, ns_collection, rel_path, dest_path, show_progress=False):

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'fileContents/%s/%s' % (ns_collection, rel_path)
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        self.logger.debug('downloading resource: %s' % rest.resource)

        # for binary data, disable the 'ACCEPT:' attribute in the http header.
        rest.accept = ''

        cb = FileIOCallback(mode='download', fpath_local=dest_path, show_progress=show_progress)

        ick = rest.doGET(cb)

        cb.close()

        if not ick:
            raise IRDMException('cannot download resource to file: %s' % rest.resource)

        return True


    def put(self, src_path, ns_collection, rel_path, show_progress=False):

        if not os.path.exists(src_path):
            raise IOError('file not found: %s' % src_path)

        # looking into the parent directory of the specified resource, for making up the destination resource path for
        # this put operation.
        paths = rel_path.split('/')

        try:
            paths.remove('.')
        except:
            pass

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'collection/%s/%s' % (ns_collection, '/'.join(paths[0:len(paths)-1]))
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        rest.params.append('listType=both')
        rest.params.append('listing=True')
        cb = SimpleCallback()
        ick = rest.doGET(cb, ignoreError=True)

        # making up the destination resource path
        dest_resource = 'fileContents/%s/%s' % (ns_collection, rel_path)
        if ick:
            children = []
            try:
                children = self.__collection_children_list__(json.loads(cb.contents)['children'])
            except KeyError, e:
                pass

            # the parent directory exists, checks if the full resource also presented as a collection or a dataObject
            for c in children:
                if paths[-1] == c['pathOrName'].split('/')[-1]:
                    if c['objectType'] == 'COLLECTION':
                        dest_resource = '%s/%s' % (dest_resource, os.path.basename(src_path))
                    break
                else:
                    continue
        else:
            # the parent directory does not seem to exist. Try to create it !!
            self.mkdir(ns_collection, '/'.join(paths[0:len(paths)-1]))

        # performs data uploading to the determined resource destination
        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = dest_resource
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        rest.params.append('force=True')

        self.logger.debug('uploading to resource: %s' % rest.resource)
        cb = FileIOCallback(mode='upload', fpath_local=src_path, show_progress=show_progress)

        ick = rest.doPOST(cb, file=['uploadFile', src_path])

        cb.close()

        if not ick:
            raise IRDMException('cannot upload file to resource: %s' % rest.resource)

        return True

    def __rdm_exec_rule__(self, irule_script, inputs, output="*out", outfmt='json', admin=False):

        ## readin content of irule_script
        if not os.path.exists(irule_script):
            raise IRDMException('file not found: %s' % irule_script)

        f = open(irule_script, 'r')
        s = f.read()
        f.close()

        ## compose data for POST
        d = { "ruleProcessingType": "INTERNAL", 
              "ruleAsOriginalText": s,
              "irodsRuleInputParameters": [] }
        
        for k,v in inputs.iteritems():
            d["irodsRuleInputParameters"].append({"name": "%s" % '*'+k, "value": "%s" % str(v).replace('%','&#37;')});

        self.logger.debug('rule data: %s' % repr(d))

        ## run RESTful POST
        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.irods_username, password=self.irods_password)
        rest.resource = 'rule'
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        cb = SimpleCallback()
        ick = rest.doPOST(cb, data=d)

        if not ick:
            raise IRDMException('cannot execute rule: %s' % irule_script)
       
        ## extract the output parameter *out 
        out = []
        try:
            self.logger.debug(cb.contents)
            out = filter(lambda x:x['parameterName']==output, json.loads(cb.contents)['outputParameterResults'])
        except KeyError:
            pass

        if not out: 
            raise IRDMException('cannot find expected output of rule: ' % irule_script)

        if outfmt == 'json':
            return json.loads(out[0]['resultObject'])
        else:
            return out[0]['resultObject'].strip('\n').split('\n')

    def __collection_children_list__(self, data):

        children = []

        # NOTE: if there is only one item in the collection, the children is presented as a dictionary rather than
        #       a list. Check the type and always convert into list.
        if isinstance(data, list):
            children = data
        elif data:
            children.append(data)
        else:
            pass

        return children

    def __getTemporaryPassword__(self, irods_username):
        """
        retrieves a temporary password for a irods user, using the irods_admin account
        :param irods_username: the irods username
        :return: the temporary password in plain-text valid for one iRODS access operation, None if failed
        """
        temp_passwd = None

        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.config.get('RDM', 'irods_admin_username'),
                           password=self.config.get('RDM', 'irods_admin_password'))
        rest.resource = 'user/%s/temppassword' % irods_username
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        rest.params.append('admin=True')
        cb = SimpleCallback()
        ick = rest.doPUT(cb)

        if ick:
            temp_passwd = json.loads(cb.contents)['password']

        return temp_passwd

    def __irods_collection_get_id_from_ns__(self, ns_collection):
        rest = IRESTful(self.config.get('RDM', 'irods_rest_endpt'), lvl=self.lvl)
        rest.httpBasicAuth(username=self.config.get('RDM', 'irods_admin_username'),
                           password=self.config.get('RDM', 'irods_admin_password'))

        rest.resource = 'collection/%s' % ns_collection
        rest.cainfo = self.irods_rest_servercert
        if not rest.cainfo:
            rest.ignore_ssl_cert_check = True

        cb = SimpleCallback()
        ick = rest.doGET(cb)

        if not ick:
            raise IRDMException('cannot retrieve collection id: %s' % rest.resource)

        return json.loads(cb.contents)['irods-rest.collection']['@collectionId']


class IRDMIcommand(IRDM):
    """
    RDM interface implementation using iCommands
    """

    def __init__(self, config, login=True, lvl=0):
        """
        initalizer with configuration file.
        """
        IRDM.__init__(self, config, lvl=lvl)
        self.IF_TYPE = 'iCommands'
        self.files_to_cleanup = []

        # initialise iRODS credentials for icommands
        self.admin_shell = None
        self.shell = None

        if login:
            try:
                self.login()
            except Exception,e:
                self.logger.error('user not logged in')

    def __del__(self):
        """
        destructor function
        """
        for f in self.files_to_cleanup:
            if os.path.exists(f):
                os.unlink(f)

    def login(self):
        # initiate the embedded admin Shell with env. setup for iCommands
        try:
            self.admin_shell = self.__getShell__(admin=True)
        except Exception,e:
            self.logger.warn('rods_admin not logged in, not harmful for regular user')

        # initiate the embedded Shell with env. setup for iCommands
        self.shell = self.__getShell__()
        self.is_user_login = True

    def logout(self):
        self.admin_shell = None
        self.shell = None
        self.__del__()
        self.is_user_login = False

    def ls(self, ns_collection, rel_path='', recursive=False):

        ns_collection = self.__make_proper_ns_collection__(ns_collection)
        rel_path = self.__make_proper_rel_path__(rel_path) 

        match_coll_name = ns_collection
        if rel_path:
            match_coll_name = os.path.join(ns_collection, rel_path)

        match_clause = 'COLL_NAME = \'%s\'' % re.sub(r'/+$','',match_coll_name)
        if recursive: 
            match_clause = 'COLL_NAME like \'%s%%\'' % re.sub(r'/+$','',match_coll_name)

        irods_files = []

        qry = 'select COLL_NAME, DATA_NAME, DATA_OWNER_NAME, DATA_SIZE, DATA_CREATE_TIME, DATA_MODIFY_TIME, DATA_CHECKSUM WHERE %s' % match_clause

        self.logger.debug('iRODS query: %s' % qry)

        cmd = 'iquest --no-page "%%s,%%s,%%s,%%s,%%s,%%s,%%s" "%s"' % qry

        output = self.__exec_shell_cmd__(cmd, timeout=180, admin=False)

        file_data = {}

        # parsing iquery output into IrodsFile object
        for l in output.split('\n'):
            d = l.strip().split(',')
            _f = IrodsFile(COLL_NAME=d[0],
                           DATA_NAME=d[1],
                           DATA_OWNER_NAME=d[2],
                           DATA_SIZE=d[3],
                           DATA_CREATE_TIME=d[4],
                           DATA_MODIFY_TIME=d[5],
                           DATA_CHECKSUM=d[6])

        # return only the unique IrodsFile objects (i.e. remove replications)
        return list(set(irods_files))

    def mkdir(self, ns_collection, rel_path):

        ns_collection = self.__make_proper_ns_collection__(ns_collection) 
        rel_path = self.__make_proper_rel_path__(rel_path) 

        cmd = 'imkdir -p %s/%s' % (ns_collection, rel_path)
        out = self.__exec_shell_cmd__(cmd, timeout=60, admin=False)

        return True

    def get(self, ns_collection, rel_path, dest_path, show_progress=False):
        pass

    def put(self, src_path, ns_collection, rel_path, show_progress=False):

        if not os.path.exists(src_path):
            raise IOError('file not found: %s' % src_path)

        ns_collection = self.__make_proper_ns_collection__(ns_collection) 
        rel_path = self.__make_proper_rel_path__(rel_path) 

        # get collections and objects within the ns_collection
        irods_files = self.ls(ns_collection, recursive=True)

        self.logger.debug('number of files: %d' % len(irods_files))

        cols = list(Set(map(lambda x:x.COLL_NAME, irods_files) + [ns_collection]))
        objs = map(lambda x:os.path.join(x.COLL_NAME, x.DATA_NAME), irods_files)

        dest_path = os.path.join(ns_collection, rel_path)

        if dest_path in cols:
            # the dest_path refers to an existing collection
            dest_path = os.path.join(dest_path, os.path.basename(src_path))

        elif dest_path in objs:
            # object already presented, do nothing as we will overwrite it
            pass

        else:
            # the dest_path is not existing, try create a directory up to its parent before upload
            self.irods_mkdir(dest_path)

        cmd = 'iput -f -v %s %s' % (src_path, dest_path)
        out = self.__exec_shell_cmd__(cmd, admin=False)
        return True

    def rmdir(self, ns_collection, rel_path, force=False):
        pass

    def rm(self, ns_collection, rel_path, force=False):
        pass

    def adminSetUserCollectionRole(self, irods_userid, ns_collection, role):

        # firstly check if the user issuing the command is irods or an authorised person
        coll_id = self.__irods_collection_get_id_from_ns__(ns_collection)
        if not coll_id:
            raise IRDMException('collection not found: %s' % ns_collection)
        role_name = '%s_%s' % (coll_id, role)

        # resolve the organisation unit name under which collection is organised
        ou_name = self.__rdm_collection_get_ou_from_ns__(ns_collection)
        ou_admins = self.__irods_group_get_members__('%s_admin' % ou_name)
        coll_managers = self.__irods_group_get_members__('%s_manager' % coll_id)

        authorised = ['irods#%s' % self.config.get('RDM', 'irodsZone')] + ou_admins

        if role not in ['reviewer']:
            authorised += coll_managers

        user = '%s#%s' % (self.config.get('RDM', 'irodsUserName'), self.config.get('RDM', 'irodsZone'))
        if user not in authorised:
            raise IRDMException('user %s not authorised' % self.config.get('RDM', 'irodsUserName'))

        # check whether the targeting user exists
        if not self.__irods_user_exists__(irods_userid):
            raise IRDMException('user not found: %s' % irods_userid)

        # check whether the user is already in any roles of the collection
        roles = filter(lambda x:x.find(coll_id) == 0, self.__irods_user_get_memberships__(irods_userid))

        if role_name in roles:
            self.logger.warn('user %s already in %s role: %s' % (irods_userid, role, role_name))
            return True

        # remove existing role of the targeting user in the collection
        for r in roles:
            authorised = ['irods#%s' % self.config.get('RDM', 'irodsZone')] + ou_admins

            if r not in ['reviewer']:
                authorised += coll_managers

            if user in authorised:
                self.__irods_group_remove_member__(r, irods_userid)
            else:
                self.logger.warn('%s not authorised to remove user from %s role'  % (self.config.get('RDM', 'irodsUserName'), r))

        # add new role of the targeting user in the collection
        if role and role != 'null':
            self.__irods_group_add_member__(role_name, irods_userid)

        return True

    def adminGetUserCollectionRole(self, irods_userid, ns_collection):

        # check whether the targeting user exists
        if not self.__irods_user_exists__(irods_userid):
            raise IRDMException('user not found: %s' % irods_userid)

        # get id of ns_collection
        id_coll = self.__irods_collection_get_id_from_ns__(ns_collection)

        if not id_coll:
            raise IRDMException('collection not found: %s' % ns_collection)

        # get user's group membership
        roles = ['null']
        members = filter(lambda x:x.find(id_coll) == 0, self.__irods_user_get_memberships__(irods_userid))
        if members:
            roles = map(lambda x:x.split('_')[1], members)

        return roles

    def adminGetUserRoles(self, irods_userid):

        # check whether the targeting user exists
        if not self.__irods_user_exists__(irods_userid):
            raise IRDMException('user not found: %s' % irods_userid)

        roles = {}

        for m in self.__irods_user_get_memberships__(irods_userid):

            # TODO: this may be simplified if all groups are named with collection id as prefix
            role_function = self.__rdm_get_role_function__(m)
            role_scope = self.__rdm_get_role_scope__(m)

            # TODO: this switch may be removed if all groups are named with collection id as prefix
            if re.match('^[0-9]+$', role_scope):
                ns_coll = self.__irods_collection_get_ns_from_id__(role_scope)
            else:
                ns_coll = role_scope

            if ns_coll not in roles.keys():
                roles[ns_coll] = []

            roles[ns_coll].append(role_function)

        return roles

    def adminGetUserRolesInScope(self, irods_userid, scope):

        myscope = self.__rdm_resolve_scope__(scope)

        # get user's group membership, the scope given by user is preserved in the dictionary keys
        roles = {scope: ['null']}
        members = filter(lambda x:self.__rdm_get_role_scope__(x) == myscope, self.__irods_user_get_memberships__(irods_userid))
        if members:
            roles[scope] = map(lambda x:self.__rdm_get_role_function__(x), members)

        return roles

    def __irods_collection_get_id_from_ns__(self, ns_collection):

        cmd = 'iquest "select COLL_ID where COLL_NAME = \'%s\'" | grep "COLL_ID" | awk -F \'=\' \'{print $NF}\'' % ns_collection

        output = self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

        ns = None
        if output:
            ns = str.strip(output)

        return ns

    def __irods_collection_get_ns_from_id__(self, id_collection):

        cmd = 'iquest "select COLL_NAME where COLL_ID = \'%s\'" | grep "COLL_NAME" | awk -F \'=\' \'{print $NF}\'' % id_collection

        output = self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

        id = None
        if output:
            id = str.strip(output)

        return id

    def __irods_user_exists__(self, irods_userid):

        cmd = 'iadmin lu %s | grep \'user_id\'' % irods_userid

        ck = False
        try:
            self.__exec_shell_cmd__(cmd, timeout=60, admin=True)
            ck = True
        except ICommandError, e:
            pass

        return ck

    def __irods_user_get_memberships__(self, irods_userid):

        cmd = 'iuserinfo %s | egrep -i \'member of group:\s+.*\' | awk \'{print $NF}\'' % irods_userid
        output = self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

        members = []
        if output:
            members = map(lambda x:x.strip(), output.split('\n'))

        # try to remove the group name that is identical to the user id
        try:
            members.remove(irods_userid)
        except ValueError,e:
            pass

        return members

    def __irods_group_get_members__(self, irods_group):

        cmd = 'iadmin lg %s' % irods_group
        output = self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

        members = []
        if output:
            # member should be listed as <uid>#<zone>, other output lines should be ignored
            members = filter(lambda x:re.match('^\S+#\S+$',x), map(lambda x:x.strip(), output.split('\n')))

        return members

    def __irods_group_add_member__(self, irods_group, irods_userid):

        cmd = 'iadmin atg %s %s' % (irods_group, irods_userid)
        self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

    def __irods_group_remove_member__(self, irods_group, irods_userid):

        cmd = 'iadmin rfg %s %s' % (irods_group, irods_userid)
        self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

    def __rdm_get_roles_as_groups__(self, scope):

        grp_prefix = '%s_' % self.__rdm_resolve_scope__(scope)

        cmd = 'iadmin lg | egrep -i \'^%s.*\'' % grp_prefix
        output = self.__exec_shell_cmd__(cmd, timeout=60, admin=True)

        groups = []
        if output:
            groups = map(lambda x:x.strip(), output.split('\n'))

        return groups

    def __rdm_exec_rule__(self, irule_script, inputs, output="\*out", outfmt='json', admin=False):

        if not os.path.exists(irule_script):
            raise IOError('file not found: %s' % irule_script)

        cmd = 'irule -F %s ' % irule_script

        for k,v in inputs.iteritems():
            cmd += ' %s="\'%s\'" ' % ('*'+k, v)

        out = self.__exec_shell_cmd__(cmd, admin=admin)

        if outfmt == 'json':
            return json.loads(re.sub('%s\s+=\s+' % output,'',out), encoding='utf-8')
        else:
            return out.strip('\n').split('\n')

    def __make_proper_ns_collection__(self, ns_collection):
        """
        removes tailing / on the ns_collection specification
        """
        return re.sub(r'/+$', '', ns_collection)

    def __make_proper_rel_path__(self, rel_path):
        """
        removes heading / on the rel_path specification
        """
        return re.sub(r'^/+', '', rel_path)

    def __exec_shell_cmd__(self, cmd, timeout=None, admin=False):

        self.logger.debug('iRODS command: %s ' % cmd)

        s = None
        if admin:
            s = self.admin_shell
        else:
            s = self.shell

        if not s:
            raise IRDMException('invalid iRODS user credential')

        rc, output, m = s.cmd1(cmd, capture_stderr=True, timeout=timeout)

        if rc != 0:
            raise ICommandError(cmd, rc, output)

        return str.strip(output)

    def __getShell__(self, admin=False):
        """
        creates a embedded Shell object with proper setting for iCommands environment
        The created Shell expects that the irodsAuthFileName is presented and
        contains valid credential for iCommands to work.
        :param admin: set True to create a shell with authenticated irods_admin account.
        :return: the Shell object
        """

        irods_env = {}
        irods_env['irods_host'] = self.config.get('RDM', 'irodsHost')
        irods_env['irods_port'] = int(self.config.get('RDM', 'irodsPort'))
        irods_env['irods_zone_name'] = self.config.get('RDM', 'irodsZone')
        irods_env['irods_home'] = self.config.get('RDM', 'irodsHome')

        # only use PAM for non-admin user credential
        if self.config.get('RDM', 'irodsAuthScheme') in ['PAM'] and not admin:
            irods_env['irods_authentication_scheme'] = self.config.get('RDM', 'irodsAuthScheme')
            irods_env['irods_ssl_ca_certificate_file'] = self.config.get('RDM', 'irodsSSLCACertificateFile')
            irods_env['irods_ssl_verify_server'] = 'cert'
        else:
            irods_env['irods_authentication_scheme'] = 'native' 

        authCached = self.config.getboolean('RDM', 'irodsAuthCached')
        myUsername = None
        myPassword = None
        if admin:
            myUsername = self.config.get('RDM', 'irods_admin_username')
            myPassword = self.config.get('RDM', 'irods_admin_password')
            myAuthfile = self.config.get('RDM', 'irods_admin_authfile')
        else:
            myUsername = self.config.get('RDM', 'irodsUserName')
            myPassword = self.config.get('RDM', 'irodsPassword')
            myAuthfile = self.config.get('RDM', 'irodsAuthFileName')

        # never cache auth token for rods admin account
        if myUsername in ['irods']:
            authCached = False

        # try to create directory for storing myAuthfile 
        try:
            os.mkdir( os.path.dirname(myAuthfile) )
        except OSError:
            pass

        irods_env['irods_user_name'] = myUsername
        irods_env['irods_authentication_file'] = myAuthfile

        # dump irods_env to a shell-specific irods_environment json file
        f = NamedTemporaryFile('w',prefix='irods_environment_',delete=False)

        os.environ['IRODS_ENVIRONMENT_FILE'] = f.name
        f.write(json.dumps(irods_env, indent=4))
        f.close()
   
        if os.path.exists(myAuthfile) and authCached and not admin:
            self.logger.debug('skip iRODS login, using existing credential: %s' % myAuthfile)
            pass
        else:

            # try to ask password from stdin if it's unavailable
            if not myPassword:
                myPassword = inputPassword('iRODS %s password (%s)' % (myUsername, irods_env['irods_authentication_scheme']))

            # running iinit via pexpect module
            cmd = '/bin/bash -c "module load irods; iinit"'
            child = pexpect.spawn(cmd)
            child.expect('assword:')
            child.sendline(myPassword)
            child.expect(pexpect.EOF, timeout=None)
            child.close()

            # iinit process returns non-zero exit code 
            if child.exitstatus != 0:
                for l in child.before.split('\n'):
                    self.logger.error(l)
                raise ICommandError(cmd, child.exitstatus, 'cannot initialise iRODS credential for user: %s' % myUsername)

            # iinit process gets terminated 
            if child.signalstatus:
                raise ICommandError(cmd, child.signalstatus, 'interrupted iRODS credential initalisation for user: %s' % myUsername)

        # files to be cleaned up in the destructor
        self.files_to_cleanup.append(os.environ['IRODS_ENVIRONMENT_FILE'])
        if not authCached:
            self.files_to_cleanup.append(irods_env['irods_authentication_file'])

        return Shell(setup_m='irods', debug=(self.lvl == 3))
