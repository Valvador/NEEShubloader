import os
import subprocess


def encrypt(needs_encryption):
    '''Encrypts string based on NEEShub's specifications on RSA encoding of passwords and usernames.
    This allows logins to remain more secure on unsecure locations, such as the FTP server. Original code
    written by Paul Hegarty over an email...'''
    check_req()
    check_key()
    generate_ssl(needs_encryption)

    
    pre_string = open('sslGenerated.bin').read().encode('base64')
    pre_string = "%%%" + pre_string.replace('\n','')
    final_string = pre_string.replace('+','_').replace('/','-')
    return final_string

def generate_ssl(enc_str):
    '''Envokes a shell command using openssl to encode an input string based on a public key.'''
    cmd = "echo '" + enc_str + "' | openssl rsautl -encrypt -inkey encryption/neespub.key -pubin > sslGenerated.bin"
    os.system(cmd)   
    
def check_req():
    '''Checks for system installation of OpenSSL'''
    try:
        subprocess.check_output(['which','openssl'])
    except:
        raise ReqError('MISSING OPENSSL, PLEASE INSTALL')
        
def check_key():
    '''Checks for a public key for encoding access to NEESHUB'''
    cwd     = os.getcwd()
    if not os.path.exists(cwd + '/encryption/neespub.key'):
        raise ReqError('Missing Public Key!')



class Error(Exception):
    '''Defines basic error class'''
    pass
        

class ReqError(Error):
    '''Raise error with custom message.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    
         