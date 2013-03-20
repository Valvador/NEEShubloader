## {{{ http://code.activestate.com/recipes/146306/ (r1)

from config import *

#
#TODO: CREATE GENERIC MULTIPART SUBROUTINES
#THIS WILL ALLOW FOR FILES TO BE UPLOADED REGARDLESS OF FILETYPES.
#
#

    


def generate_upload_xml(filename, path):
    '''Basic XML generation for any file you would be uploading to
    the NEEShub. All other XML generating functions for file uploads
     must call this function first.'''
    xml_string      = """
                    <DataFile viewable="MEMBERS">
                        <name>%s</name>
                        <path>%s</path>
                    </DataFile>""" % (filename, path)
    return xml_string



def encode_multipart_formdata(xml_sheet, filename, username, password):
    """
    xml_string is a sequence of (name, value) elements for regular form xml_string.
    file is a sequence of (name, filename, value) elements for data to be uploaded as file
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY    = '----------boUnDary2013nEes_$'
    CRLF        = '\r\n'
    L           = []
    
    # BEGIN MESSAGE
    
    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="GAsession"') #% key_xml)
    gasession = '%s/%s' % (username,password)
    L.append('')
    L.append(gasession)

    
    L.append('--' + BOUNDARY)
    L.append('Content-Type: %s' % get_content_type())
    L.append('Content-Disposition: form-data; name="fileup"; filename="%s"' % (filename,))
    L.append('')
    L.append('')


    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="message"') #% key_xml)
    L.append('')
    L.append(xml_sheet)

    # CLOSE MESSAGE    
    
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body            = CRLF.join(L)
    content_type    = 'multipart/form-data ; boundary=%s' % BOUNDARY
    return content_type, body




def get_content_type():
    return 'application/octet-stream'
## end of http://code.activestate.com/recipes/146306/ }}}

#
#    SPECIFIC XML'S GENERATED
#

def generate_file_xml(filename, expnum, trialnum, ext):
    '''Specific XML generation method used for uploading project files to NEEShub.'''
    data_folder     = cfg_hub_ext_fold[ext]
    path            = "/nees/home/%s/Experiment-%s/Trial-%s/Rep-1/%s" % (nees_prj_id, expnum, trialnum, data_folder) 
    xml_string      = generate_upload_xml(filename, path)
    return xml_string

def generate_report_xml(filename, expnum, trialnum):
    '''Specific XML generation method used for uploading report files to NEEShub.'''
    path            = '/nees/home/%s/Experiment-%s/Trial-%s/Documentation' % (nees_prj_id, expnum, trialnum)
    xml_string      = generate_upload_xml(filename, path)
    return xml_string


#
# DEBUG/OBSOLUTE
#

def generate_paths(expnum, trialnums, ext='.msd'):
    
    paths = []
    for trialnum in trialnums:    
        path          = "/nees/home/%s/Experiment-%s/Trial-%s/Rep-1/Converted_Data" % (nees_prj_id, expnum, trialnum)
        paths.append(path)
    return paths
        
        
def generate_upload_xmls(filenames, paths):
    '''Basic XML Generation function for multiple XMLs in an attempt to create
    a multi-file upload.'''
    xmls        = []
    if len(filenames) == len(paths):
        for i in range(len(filenames)):
            filename    = filenames[i]
            path        = paths[i]
            xml_string  = generate_upload_xml(filename, path)
            xmls.append(xml_string)
    else:
        print 'List of Files and Paths do not match. Please try again.'
    return xmls
            
        
def encode_multipart_forms(xml_sheets, filenames, username, password):
    """
    xml_string is a sequence of (name, value) elements for regular form xml_string.
    file is a sequence of (name, filename, value) elements for data to be uploaded as file
    Return (content_type, body) ready for httplib.HTTP instance
    """
    if len(xml_sheets) == len(filenames):
        BOUNDARY    = '----------boUnDary2013nEes_$'
        CRLF        = '\r\n'
        L           = []
        
        # BEGIN MESSAGE
        
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="GAsession"') #% key_xml)
        gasession = '%s/%s' % (username,password)
        L.append('')
        L.append(gasession)
        
        # Add multi-file information to POST.
        for i in range(len(xml_sheets)):
            
            xml_sheet   = xml_sheets[i]
            filename    = filenames[i]
            
            L.append('--' + BOUNDARY)
            L.append('Content-Type: %s' % get_content_type())
            L.append('Content-Disposition: form-data; name="fileup"; filename="%s"' % (filename,))
            L.append('')
            L.append('')
    
    
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="message"') #% key_xml)
            L.append('')
            L.append(xml_sheet)
    
        # CLOSE MESSAGE    
        
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body            = CRLF.join(L)
        content_type    = 'multipart/form-data ; boundary=%s' % BOUNDARY
        return content_type, body
    else:
        print "Number of XMLs and files do not match. STOPPING"   #TODO: ADD ERROR RAISE.
          
        
        