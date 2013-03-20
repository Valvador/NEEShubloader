#Basic FTP Module to designed to abstract a ftplib layer to a somewhat low level.
#Created by Val Gorbunov for the use of NEES@UCSB

#Created by Val Gorbunov for the use of NEES@UCSB
from __future__ import print_function
import ftplib
import os
import time
import getpass
import socket







class ftp(object):
    '''FTP Class designed to abstract the ftplib functions.'''
    
    def __init__(self, host, username = '', password = ''):

        # If password not entered, ask for in prompt. 
        if (username == '' and password == ''):
            username    = raw_input('FTP Username:')
            password    = getpass.getpass('FTP Password:')  
        
        # Default initialization.
        self.host     = host
        self.conn     = None  
        self.username = username
        self.password = password 
        self.maxsize  = 0
        self.nowsize  = 0
        self.srcpath  = ''
        self.connect()
        
    def connect(self):
        ''' Establishes or refreshes any basic ftplib.FTP instance connections.'''
        if self.conn is not None:
            self.conn.close()
            del self.conn
            self.conn = None
        self.conn = ftplib.FTP(host     = self.host, 
                               user     = self.username,
                               passwd   = self.password, 
                               timeout  = 1200)
    
    def ls(self, path=''):
        '''Gives the list of the current directory of the FTP server.'''
        self.connect()
        if path != '':
            self.conn.cwd(path)
        self.conn.retrlines('LIST')
 
    def cwd(self, path):
        '''Gives current working directory.'''
        self.connect()
        self.conn.cwd(path)   
        
    def mkd(self, path):
        '''Creates a directory described by path.'''
        self.connect()
        self.conn.mkd(path) 

    def handle(self, block):
        ''' Upload progress report.'''
        self.nowsize += len(block)
        percent    = 100 * (float(self.nowsize) / self.maxsize)
        statement  = 'Uploading %s, %.1f percent complete.' % (self.srcpath, percent)
        print (statement, end="\r")
        
    
    def upload(self, ftp_path, source_path):
        """Establishes a binary upload to FTP server.
        Args:
            ftp_path: Location to where the file will be uploaded.
            source_path: location where the file currently resides.
        """
        self.maxsize      = os.path.getsize(source_path)
        self.srcpath      = source_path
        ufile             = open(source_path, 'rb')
        upload_cmd        = 'STOR %s' % (ftp_path,)
        #Attempt to upload files.
        while True:
            try:
                # Upload Text File-type if file is ASCII
                if source_path[-4:] == '.txt':
                    self.connect()
                    self.conn.storlines(upload_cmd, ufile, callback=self.handle)
                # Upload all other filetypes.
                else:    
                    self.connect()
                    self.conn.storbinary(upload_cmd, ufile, callback = self.handle, blocksize = 1024)
            except socket.error as ex:
                if str(ex) == "[Errno 35] Resource temporarily unavailable":
                    continue
            break
        self.nowsize = 0