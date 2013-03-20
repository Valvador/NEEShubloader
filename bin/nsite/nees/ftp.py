#Basic FTP Module to designed to abstract a ftplib layer to a NEEShub-specific layer.
#Created by Val Gorbunov for the use of NEES@UCSB
import interface.ftp as ift
import encryption.neescrypt
from config import *
import utils

unencrypted_usr = utils.hub_username
encrypted_pass  = encryption.neescrypt.encrypt(utils.hub_password)
conn            = ift.ftp(ftphost, unencrypted_usr, encrypted_pass)




def upload_to_project(filename, source_path):
    '''Simplifies the process for users of the UCSB NEES project by only
    requiring the input of a filename.'''
    ftp_path = nees_prj_fld + filename
    
    # Attempt to Upload File to your NEES Upload Folder
    try:
        conn.upload(ftp_path, source_path)

    # If folder is missing, create folder.
    except ift.ftplib.error_perm, resp:
        if str(resp) == "550 %s: No such file or directory" % (ftp_path,):
            conn.mkd(nees_prj_fld)
            upload_to_project(filename, source_path)
        else:
            raise


def upload_file(source_folder, filename, exten):
    '''Uploads a file to FTP, and does a WEBSERVICES post to NEEShub
    in order to allocate the file correctly.'''
        
    #FTP Uploading Instance
    full_filename = filename + exten
    full_pathname = source_folder + full_filename 
    conn.upload_to_project(full_filename, full_pathname)
    
def upload_files(source_folder, src_path, extensions):
    '''If a filename is given with no extension, with a list of extensions
    multiple versions of the file will be uploaded.'''
    for exten in extensions:
        filename = src_path
        conn.upload_file(source_folder, filename, exten)  