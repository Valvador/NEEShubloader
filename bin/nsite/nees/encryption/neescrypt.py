import os
import subprocess


def encrypt(needs_encryption):
    '''Encrypts string based on NEEShub's specifications on RSA encoding of passwords and usernames.
    This allows logins to remain more secure on unsecure locations, such as the FTP server. Original code
    written by Paul Hegarty over an email...'''
    check_req()
    check_key()
    generate_ssl(needs_encryption)

    key_path   = get_key_path()
    filepath   = key_path + 'sslGenerated.bin'    
    pre_string = open(filepath).read().encode('base64')
    pre_string = "%%%" + pre_string.replace('\n','')
    final_string = pre_string.replace('+','_').replace('/','-')
    return final_string

def generate_ssl(enc_str):
    '''Envokes a shell command using openssl to encode an input string based on a public key.'''
    key_path = get_key_path()
    cmd = "echo '%s' | openssl rsautl -encrypt -inkey %sneespub.key -pubin > %ssslGenerated.bin" % (enc_str, key_path, key_path)
    os.system(cmd)   
    
def check_req():
    '''Checks for system installation of OpenSSL'''
    output = subprocess.Popen(['which','openssl'], stdout=subprocess.PIPE).communicate()[0]
    if output == '':
        raise ReqError('MISSING OPENSSL, PLEASE INSTALL')
        
def check_key():
    '''Checks for a public key for encoding access to NEESHUB'''
    key_path    = get_key_path()
    if not os.path.exists(key_path + 'neespub.key'):
        raise ReqError('Missing Public Key!')

def get_key_path():
    '''Gets path of the encryption folder, where this is located.'''
    module_path     = os.path.dirname(__file__)
    file_path       = os.path.abspath(__file__)
    path_index      = file_path.find(module_path) + len(module_path)
    key_path        = file_path[:path_index]
    if key_path != '':
        key_path += '/'
    return key_path

class Error(Exception):
    '''Defines basic error class'''
    pass
        

class ReqError(Error):
    '''Raise error with custom message.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    
         