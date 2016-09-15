import base64
import json
import os
import re
import pycurl
import urllib
from clint.textui import progress
from Logger import getLogger

class SimpleCallback:
    """simple callback class for pyCURL"""

    def __init__(self):
        self.header = ''
        self.contents = ''

    def header_callback(self, buf):
        self.header = self.header + buf

    def body_callback(self, buf):
        self.contents = self.contents + buf

    def progress_callback(self, download_t, download_d, upload_t, upload_d):
        pass
        #print 'total to upload', upload_t
        #print 'total uploaded', upload_d


class FileIOCallback(SimpleCallback):
    """callback class with dynamic progress bar for file uploading and downloading"""

    def __init__(self, mode, fpath_local, show_progress=True):

        # TODO: use new style constructor inheritance
        SimpleCallback.__init__(self)

        self.fd = None
        self.mode = mode
        self.content_length = 0
        self.c_transferred = 0
        self.r_transferred = 0
        self.bar = None

        if show_progress:
            self.bar = progress.Bar(label='%s ' % os.path.basename(fpath_local), expected_size=100)

        # for file upload, we use the HTTPPOST to post a form rather than reading file content
        if self.mode == 'download':
            self.fd = open(fpath_local, 'wb')

    def header_callback(self, buf):
        self.header = self.header + buf
        re_cnt_length = re.compile(r'Content-Length:\s+([0-9]*)$')
        m = re_cnt_length.match(buf.strip())
        if m:
            self.content_length = long(m.group(1))

    def body_callback(self, buf):
        if self.mode == 'download':
            self.fd.write(buf)
        else:
            SimpleCallback.body_callback(self, buf)

    def progress_callback(self, download_t, download_d, upload_t, upload_d):

        total_size = self.content_length
        if self.mode == 'upload':
            # get total size of transfer from upload_t
            total_size = upload_t

            if upload_d != self.c_transferred:
                self.c_transferred = upload_d
        else:
            if download_d != self.c_transferred:
                self.c_transferred = download_d

        if total_size:
            r = int(100 * self.c_transferred / total_size)
            if r != self.r_transferred:
                if self.bar:
                    self.bar.show(r)
                self.r_transferred = r
        else:
            if self.bar:
                self.bar.show(0)

    def close(self):
        if self.fd:
            self.fd.close()
        if self.bar:
            self.bar.done()


class IRESTful:
    """ Interface class implementing RESTful calls using pyCURL library.
    """

    def __init__(self, baseURL='', lvl=0):
        """
        Object initializer
        :param baseURL: base URL of the RESTful endpoint
        :param callback: objects containing callback functions for pyCURL
        :param lvl: logging level
        :return:
        """

        self.logger = getLogger(lvl=lvl)
        self.auth = ''
        self.baseURL = baseURL
        self.resource = ''
        self.params = []
        self.requestMethod = 'GET'
        self.accept = 'application/json'
        self.contentType = ''
        self.ssl_verifypeer = 1
        self.ssl_verifyhost = 2
        self.cainfo = ''
        self.ignore_ssl_cert_check = False

    def httpBasicAuth(self, username, password):
        """
        sets username and password for http basic authorisation
        :param username: the username
        :param password: the password in plaintext
        :return:
        """
        self.auth = 'Authorization: Basic %s' % base64.b64encode("%s:%s" % (username, password))

    def __makeEndpoint__(self):
        """
        composes the RESTful endpoint
        :return: the RESTful endpoint in string
        """

        endpoint = self.baseURL

        if self.resource:
            endpoint += '/%s' % urllib.quote(self.resource)

        if self.params:
            endpoint += '?%s' % '&'.join(self.params)

        return endpoint

    def __prepareCurlObj__(self, callback):
        """
        prepares the CurlObj for making RESTful call
        :return: the prepared pycurl object
        """

        http_header = []

        if self.accept:
            http_header.append('ACCEPT: %s' % self.accept)

        if self.auth:
            http_header.append(self.auth)

        if self.contentType:
            http_header.append('Content-Type: %s' % self.contentType)

        c = pycurl.Curl()
        c.setopt(c.URL, self.__makeEndpoint__())
        c.setopt(c.CUSTOMREQUEST, self.requestMethod)
        c.setopt(c.HEADERFUNCTION, callback.header_callback)
        c.setopt(c.WRITEFUNCTION, callback.body_callback)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, callback.progress_callback)
        c.setopt(c.HTTPHEADER, http_header)

        if self.ignore_ssl_cert_check:
            c.setopt(c.SSL_VERIFYPEER, 0)
            c.setopt(c.SSL_VERIFYHOST, 0)
        else:
            c.setopt(c.CAINFO, self.cainfo)
            c.setopt(c.SSL_VERIFYPEER, self.ssl_verifypeer)
            c.setopt(c.SSL_VERIFYHOST, self.ssl_verifyhost)

        return c

    def doGET(self, callback, ignoreError=False):
        """
        performs GET request to endpoint
        :return: True if success
        """
        self.requestMethod = 'GET'
        self.contentType = ''

        c = self.__prepareCurlObj__(callback)
        c.perform()

        ick = self.__http_ok__(c)
        if not ick:
            if not ignoreError:
                self.logger.error(callback.header)
        else:
            self.__print_callback_contents__(callback)

        c.close()

        return ick

    def doPUT(self, callback, data=None, ignoreError=False):
        """
        performs PUT request to endpoint
        :param data: HTTP data in dictionary for PUT
        :return: True if success
        """
        self.requestMethod = 'PUT'

        if data:
            self.contentType = 'application/json'

        c = self.__prepareCurlObj__(callback)

        if data:
            c.setopt(c.POSTFIELDS, json.dumps(data))
        c.perform()

        ick = self.__http_ok__(c)
        if not ick:
            if not ignoreError:
                self.logger.error(callback.header)
        else:
            self.__print_callback_contents__(callback)

        c.close()

        return ick

    def doPOST(self, callback, data=None, file=None, ignoreError=False):
        """
        performs POST request to endpoint
        :param data: HTTP data in dictionary for POST
        :param file: ('FORM FILED', 'FILE PATH') tuple for file uploading
        :return: True if success
        """

        self.requestMethod = 'POST'

        if data:
            self.contentType = 'application/json'

        c = self.__prepareCurlObj__(callback)

        if data:
            c.setopt(c.POSTFIELDS, json.dumps(data))

        if file:
            form_data = [(file[0], (c.FORM_FILE, file[1], c.FORM_CONTENTTYPE, 'application/octet-stream'))]
            c.setopt(c.HTTPPOST, form_data)

        c.perform()

        ick = self.__http_ok__(c)
        if not ick:
            if not ignoreError:
                self.logger.error(callback.header)
        else:
            self.__print_callback_contents__(callback)

        c.close()

        return ick

    def doDELETE(self, callback, ignoreError=False):
        """
        performs DELETE request to endpoint
        :return: True if success
        """
        self.requestMethod = 'DELETE'
        self.contentType = ''

        c = self.__prepareCurlObj__(callback)
        c.perform()

        ick = self.__http_ok__(c)
        if not ick:
            if not ignoreError:
                self.logger.error(callback.header)
        else:
            self.__print_callback_contents__(callback)

        c.close()

        return ick

    def __print_callback_contents__(self, callback):
        """
        common function to print callback contents after making the cURL call
        :param callback: the callback object
        :return:
        """

        try:
            self.logger.debug(json.dumps(json.loads(callback.contents), indent=4, sort_keys=True, separators=(',', ':')))
        except Exception, e:
            self.logger.debug('callback contents is empty or not in JSON format.')

    def __http_ok__(self, curlObj):
        """
        evaluates the HTTP code in the HTTP header
        :param curlObj: the curl object that performs an HTTP connection
        :return: True if the HTTP_CODE is lower than 400; otherwise False
        """
        return curlObj.getinfo(pycurl.HTTP_CODE) < 400
