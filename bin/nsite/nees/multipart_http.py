## {{{ http://code.activestate.com/recipes/146306/ (r1)



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

def generate_file_xml(filename, hub_project_id, expnum, trialnum, rep_num, data_folder):
    '''Specific XML generation method used for uploading project files to NEEShub.'''
    path            = "/nees/home/%s/Experiment-%s/Trial-%s/Rep-%s/%s" % (hub_project_id, expnum, trialnum, rep_num, data_folder) 
    xml_string      = generate_upload_xml(filename, path)
    return xml_string

def generate_report_xml(filename, hub_project_id, expnum, trialnum):
    '''Specific XML generation method used for uploading report files to NEEShub.'''
    path            = '/nees/home/%s/Experiment-%s/Trial-%s/Documentation' % (hub_project_id, expnum, trialnum)
    xml_string      = generate_upload_xml(filename, path)
    return xml_string

