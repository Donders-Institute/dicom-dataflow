#!/usr/bin/env python

import os
import sys
import re
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from Logger import getLogger

class SMTPMailer:

    def __init__(self, host='localhost', port=25, credential=None, lvl=0):

        self.smtp_host = host
        self.smtp_port = port
        self.credential = credential

        self.logger = getLogger(name=self.__class__.__name__, lvl=lvl)

    def sendMultipartEmail(self, subject, fromAddress, toAddress, parts):
        """
        sends multipart email
        :param subject: subject of the email
        :param fromAddress: from address of the email
        :param toAddress: to address of the email
        :param parts: parts with key of the MIME type and value of content
        :return:
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = fromAddress
        msg['To'] = toAddress

        for k,v in parts.iteritems():
            msg.attach(MIMEText(v.encode('utf-8'), k, 'utf-8'))

        # connect to SMTP server and send out the message
        s = smtplib.SMTP(host=self.smtp_host, port=self.smtp_port)

        if self.credential:
            try:
                s.login(self.credential['username'], self.credential['password'])
            except KeyError, e:
                # no username/password is given, ignore it
                self.logger.error('username or password not found in credential dict')
                raise e

        s.sendmail(fromAddress, [toAddress], msg.as_string())
        s.quit()
