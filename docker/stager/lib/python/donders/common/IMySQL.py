#!/usr/bin/env python
from common.Logger import getLogger
## loading MySQL library for updating the project database
try:
    ## using pure python MySQL client
    import MySQLdb as mdb
except Exception, e:
    ## trying mysql.connector that requires MySQL client library 
    #import mysql.connector as mdb
    #from mysql.connector import errorcode
    import pymysql as mdb

class IMySQL:

    def __init__(self, db_host, db_username, db_password, db_name, lvl=0):
        self.host = db_host
        self.uid = db_username 
        self.passwd = db_password
        self.db = db_name
        self.cnx = None
        self.logger = getLogger(lvl=lvl)
        pass

    def getConnector(self):
        ''' get MySQL connector
        '''
        if not self.cnx:
            self.__initConnector__()
        return self.cnx

    def closeConnector(self):
        ''' close MySQL connector
        '''
        try:
            self.cnx.close()
        except Exception:
            pass
        self.cnx = None

    def __initConnector__(self):
        ''' internal method to establish MySQL connector
        '''
        config = None 
 
        if mdb.__name__ in ['MySQLdb','pymysql']:
            ### use MySQLdb library
            config = {'user'   : self.uid,
                      'passwd' : self.passwd,
                      'db'     : self.db,
                      'host'   : self.host }
            try:
                self.cnx = mdb.connect(**config)
            except mdb.Error, e:
                self.logger.error('db query error %d: %s' % (e.args[0],e.args[1]))
 
                if self.cnx: self.cnx.close()
        else:
            ### use mysql-connector library
            config = {'user'             : self.uid,
                      'password'         : self.passwd,
                      'database'         : self.db,
                      'host'             : self.host,
                      'raise_on_warnings': True }
            try:
                self.cnx = mdb.connect(**config)
            except mdb.Error, err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    self.logger.error("something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    self.logger.error("database does not exists")
                else:
                    self.logger.error(err)
             
                if self.cnx: self.cnx.close()
