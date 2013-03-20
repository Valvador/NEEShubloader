#Created by Val Gorbunov for the use of NEES@UCSB
import ftplib
import os
import neescrypt
import time
import getpass
from config import *

class NEESftp(object):
    '''FTP Class designed to function like an intermediary between the user
    and the NEEShub ftp server, much like the hub_interface NEEShttp()'''
    
    def __init__(self, username = '', password = '', host = ftphost):

        # If password not entered, ask for in prompt. 
        if (username == '' and password == ''):
            username    = raw_input('NEEShub Username:')
            password    = getpass.getpass('NEEShub Password:')  
        
        # Default initialization.
        self.host     = host
        self.conn     = None  
        self.username = username
        self.password = neescrypt.encrypt(password) 
        self.connect()
        
    def connect(self):
        ''' Establishes or refreshes any basic ftplib.FTP instance connections.'''
        if self.conn is not None:
            self.conn.close()
            del self.conn
            self.conn = None
        self.conn = ftplib.FTP(host = self.host, 
                               user = self.username,
                               passwd = self.password, 
                               timeout = 1200)
    
    def ls(self):
        '''Gives the list of the current directory of the FTP server.'''
        self.conn.retrlines('LIST')
 
    def cwd(self, path):
        '''Gives current working directory.'''
        self.conn.cwd(path)    
    
    def upload(self, ftp_path, source_path):
        '''Establishes a binary upload from source_path on local machine to
        ftp_path on the server.'''
        ufile             = open(source_path, 'rb')
        upload_cmd        = 'STOR %s' % (ftp_path,)
        self.conn.storbinary(upload_cmd, ufile)
        
#---------------------------------------------------------------------------------------------------------------
# IV. UPLOADING FUNCTIONALITY
#---------------------------------------------------------------------------------------------------------------

    def upload_to_project(self, filename, source_path):
        '''Simplifies the process for users of the UCSB NEES project by only
        requiring the input of a filename.'''
        ftp_path = nees_prj_fld + filename
        self.upload(ftp_path, source_path)


    def upload_file(self,  source_folder, filename, exten):
        '''Uploads a file to FTP, and does a WEBSERVICES post to NEEShub
        in order to allocate the file correctly.'''
            
        #FTP Uploading Instance
        full_filename = filename + exten
        full_pathname = source_folder + full_filename 
        self.upload_to_project(full_filename, full_pathname)
        
    def upload_files(self, source_folder, src_path, extensions):
        '''If a filename is given with no extension, with a list of extensions
        multiple versions of the file will be uploaded.'''
        for exten in extensions:
            filename = src_path
            self.upload_file(source_folder, filename, exten)  
            
            


