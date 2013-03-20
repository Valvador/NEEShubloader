#Basic FTP Module to designed to abstract a mySQLdb layer to a somewhat low level.
#Created by Val Gorbunov for the use of NEES@UCSB
#Requires mySQLdb module to be accessible from the module.


from operator import itemgetter
import sys
import MySQLdb
import getpass

#---------------------------------------------------------------------------------------------------------------------------------------------------------
# I. Initialization and Basic Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------

class mySQL(object):
    '''This class instance creates a connection with the UCSB's mySQL interface. ucsbSQL becomes the defined object
    that has functions applied to it in order to perform specific tasks. Tasks such as determining which information to
    apply to each individual trial being uploaded to the NEEShub.'''
    
    def __init__(self, host, dbname):
        self.host           = host
        self.con            = None
        self.username       = raw_input('mySQL Username: ')
        self.password       = getpass.getpass('mySQL Password: ')
        self.connect(host, dbname)
        
    def connect(self, host, dbname):
        '''This module is responsible for connecting the ucsbSQL class to the mySQL database. Very basic connection
        that double checks for existing connections.'''
        if self.con is not None:
            self.con.close()
            del self.con
            self.con = None
        self.con = MySQLdb.connect(host, self.username, self.password, dbname)
        
    def request(self, request_parameters):
        '''Basic mySQL request command. This basically condenses the process of sending a mySQL
        request with a MySQLdb "cursor" object, and automatically returns the reply to the mySQL
        request.'''
        self.returned_list = []
        with self.con:
            cur = self.con.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(request_parameters)
            rows = cur.fetchall()
            for row in rows:
                self.returned_list.append(row)
        return self.returned_list
    
    