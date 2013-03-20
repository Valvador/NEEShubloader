from config import *
import getpass
import datetime
import string
#
# nees-http method utilities
#

hub_username   = raw_input('NEEShub username:')                      
hub_password   = getpass.getpass('NEEShub password:')



def authenticate_request(request_params, username = hub_username, password = hub_password):
    '''This appends a GAsession to the request parameter sent to
    the http request. Uses neeshub-specific format defined in
    config.py.'''
    #TODO: ADD ENCRYPTION METHOD
    authentic_params = neeshub_auth_format % (request_params, username, password)
    return authentic_params
    
def find_trial_id(location_string):
    '''Finds the trial id from a header returned by a post-request
    to the neeshub.'''
    id_index                = location_string.find('/Trial/')
    id_offset               = len('/Trial/')
    trial_id                = location_string[id_index+id_offset:]
    return trial_id

def find_repetition_id(location_string):
    '''Finds the repetition id from a header returned by a post-request
    to the neeshub.'''    
    id_index                = location_string.find('/Repetition/')
    id_offset               = len('/Repetition/')
    rep_id                  = location_string[id_index+id_offset:]
    return rep_id   

def find_experiment_id(location_string):
    '''Finds the trial id from a header returned by a post-request
    to the neeshub.'''
    id_index                = location_string.find('/Experiment/')
    id_offset               = len('/Experiment/')
    exp_id                = location_string[id_index+id_offset:]
    return exp_id


def is_number(s):
    '''This function is included in order to make the "get_trial_title()" function be able to check different title formats.
    This function is taken from a Stack Overflow post by Daniel Goldberg on Dec 9th, 2008 under the question "How do I
    check if a string is a number in Python?" I take no credit for this function.'''
    try:
        float(s)
        return True
    except ValueError:
        return False


#
# HTTP UTILS
#

def parse_description(keystring, data, topass = True):
    '''This is used to parse through the description string in get_trial_metadata_dictionaries_partial to find necessary data.'''
    parse_index = data.find('<description>') + len("<description>")
    s_ind = data[parse_index:].find(keystring) + len(keystring) + parse_index
    e_ind = data[s_ind:].find("\n") + s_ind
    result = data[s_ind:e_ind]
    if result == '' and topass == False:
        print "We could not find the %s in the current description format, please review it and and manually input its value." % (keystring,)
        print data
        result = raw_input('Enter the %s>>>' % (keystring,))
    return result

def generate_trial_name_xml(trial_num):
    '''Generates an XML entry with the trials name.'''
    if trial_num == '':
        xml_form = ''
    else:
        xml_form = '<name>Trial-%s</name>' % trial_num
    return xml_form
        
def generate_experiment_name_xml(exp_num):
    '''Generates an XML entry with the trials name.'''
    if exp_num == '':
        xml_form = ''
    else:
        xml_form = '<name>Experiment-%s</name>' % exp_num
    return xml_form
        
def generate_project_title_xml(title,
                               description,
                               contact_name = '',
                               contact_email = '',
                               start_date = '',
                               fundorg = '',
                               nick_name = '',
                               fund_org = '',
                               fund_org_proj = ''):
    '''Generates an XML form for the NEEShub project generation.'''
    xml_form = """
    <Project VIEW="PUBLIC" type="Structured">
        <title>%s</title>
        <description>%s</description>
        <contactEmail>%s</contactEmail>
        <contactName>%s</contactName>
        <startDate>%s</startDate>
        <status>unpublished</status>
        <sysadminName>%s</sysadminName>
        <sysadminEmail>%s</sysadminEmail>
        <nickname>%s</nickname>
        <fundorg>%s</fundorg>
        <fundorgprojid>%s</fundorgprojid>
    </Project>
    """ % (title,
           description,
           contact_email,
           contact_name,
           start_date,
           contact_name,
           contact_email,
           nick_name,
           fund_org,
           fund_org_proj)
    return xml_form
                
#
# CACHING UTILS
#                


def convert_to_float(s):
    ''' This is specifically created to help the caching process bypass invalid description structures
    when attempting to pull the caching information from the NEEShub.'''
    if is_number(s):
        return float(s)
    else: 
        return "INVALID"

def convert_to_long(s):
    ''' This is specifically created to help the caching process bypass invalid description structures
    when attempting to pull the caching information from the NEEShub.'''
    if is_number(s):
        return long(s)
    else: 
        return "INVALID"
