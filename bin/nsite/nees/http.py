#Adapts the abstracted http layer to our NEEShub-specific interfaces.
#Created by Val Gorbunov for the use of NEES@UCSB
import time
import utils
import nees_logging
import multipart_http
import threading_http
from config import *
import interface.http as ih


conn           = ih.http(httphost) 

#
# NEESHUB SPECIFIC GET FUNCTIONS
#

def get_experiment_id_dictionary(project_id):
    """Make NEEShub request for Experiment-IDs and Experiment Numbers.
    Args:
        project_id: NEEShub-given project id.
    Returns:
        dictionary of Experiment-IDs in the format of
            {'Experiment#':'ID#'...}
    """
    request             = "%s%s" % (neeshub_project_path, project_id,)
    authentic_request   = utils.authenticate_request(request)
    request_dict        = conn.request("GET", authentic_request)
    data                = request_dict['data']
    index               = 0
    experimentstring    = "%s%s/Experiment/" % (neeshub_project_path, project_id,)
    inlist              = []
    experiment_dict     = {}
    while index < len(data):                     #CHECK FOR ALL OCCURANCES OF 'EXPERIMENT-' TO LOCATE THE WEBSERVICE DATASTRUCTURE.
        index=data.find(experimentstring,index)
        if index == -1:
            break
        index += len(experimentstring)           #MOVE INDEX TO WHERE EXPERIMENT NUMBER IS
        inlist.append(index)
        endindex        = index+data[index:].find('" id=')
        name_start      = '<name>'
        name_end        = '</name>'
        text_pass       = 'Experiment-'
        name_index      = endindex + data[endindex:].find(name_start) + len(name_start) + len(text_pass)
        name_endindex   = name_index + data[name_index:].find(name_end)
        dictkey         = data[name_index:name_endindex]  
        dictval         = data[index:endindex]
        experiment_dict[dictkey] = dictval
    print inlist    
    return experiment_dict
    

def get_trial_id_dictionary(project_id, experiment_id):
    """Request Trial-IDs through HTTP Get request.
    Args:
        project_id: NEEShub Project Specific IDs
        experiment_id: NEEShub Experiment ID. Use
            get_experiment_id_dictionary to acquire.
    Returns:
        dictionary of Trial-IDs in the format of
            {'Trial-#':'ID#'...} 
    """
    request             = "%s%s/Experiment/%s" % (neeshub_project_path, project_id, experiment_id)
    authentic_request   = utils.authenticate_request(request)
    request_dict        = conn.request("GET", authentic_request) 
    data                = request_dict['data']
    index               = 0
    experimentstring    = "%s%s/Experiment/%s/Trial/"  % (neeshub_project_path, project_id, experiment_id)      
    experimentdict      = {}
    #CHECK FOR ALL OCCURANCES OF 'TRIAL-' TO FIND ALL TRIALS
    while index < len(data):                     
        index       = data.find(experimentstring,index)
        index_tnum  = data.find("Trial-",index)
        if index == -1:
            break
        index += len(experimentstring)           
        trialID     = data[index:data.find('" id',index)]
        trialNum    = data[index_tnum:data.find('</name>',index)]
        experimentdict[trialNum] = trialID
    return experimentdict          

def get_trial_metadata_dictionaries_partial(project_id, experiment_id, experimentdict):
    '''This creates a dictionary of dictionaries that is organized as such: {Trial-#:{'evid': 12345, 'magnitude': 4.02, 'distance': 124}}.
    This makes it much easier for the information stored to be parsed through by utilizing a double index to get the specific piece of 
    of information about the specific Trial.'''
    cache_evid_dict     = {}
    cache_ml_dict       = {}
    cache_distance_dict = {}
    for trial in experimentdict:
        request             = "%s%s/Experiment/%s/Trial/%s" % (neeshub_project_path, 
                                                               project_id, 
                                                               experiment_id, 
                                                               experimentdict[trial])
        authentic_request   = utils.authenticate_request(request)
        requestDict         = conn.request('GET', authentic_request)
        data                = requestDict['data']
        evid                = utils.parse_description('evid:', data)
        magnitude           = utils.parse_description('ml:', data)
        distance            = utils.parse_description('distance:', data)
        cache_evid_dict[trial]        = utils.convert_to_long(evid)
        cache_ml_dict[trial]          = utils.convert_to_float(magnitude)
        cache_distance_dict[trial]    = utils.convert_to_float(distance)
        nees_logging.log_cache_invalid_cache_variables(trial, cache_evid_dict[trial],cache_ml_dict[trial],cache_distance_dict[trial])
    return cache_evid_dict, cache_ml_dict, cache_distance_dict

def get_trial_metadata_dictionaries(project_id, experiment_id):
    """Gets metadata from trial descriptions. 
    WARNING: This requires trial description defines metadata in the
    'datatype: data' format.
    Args:
        project_id: NEEShub Project Specific IDs
        experiment_id: NEEShub Experiment ID. Use
            get_experiment_id_dictionary to acquire.
    Returns:
        3-part tuple of dictionaries. Dictionary of event ids, 
        magnitude ids and distance ids. Keys are 'Trial-#'"""
    experimentdict                  = get_trial_id_dictionary(project_id, experiment_id)
    evid_dict, ml_dict, dist_dict   = get_trial_metadata_dictionaries_partial(project_id, experiment_id, experimentdict)
    return evid_dict, ml_dict, dist_dict


def post_project(title, 
                 description, 
                 contact_name='', 
                 contact_email='', 
                 start_date='',
                 fundorg='',
                 nick_name='',
                 fund_org='',
                 fund_org_proj=''):
    """Creates a NEES webservices Project.
        Args:
        title: What you want the Project Title to be.
        description: How you'd like to describe it.
        start_date: start date
        (experiment_num): Chose experiment number 
            (RECOMMNDED TO LEAVE BLANK!)
    Returns:
        string that is the experiment id for the created experiment."""
    xml_form    = utils.generate_project_title_xml(title, 
                                                   description, 
                                                   contact_name, 
                                                   contact_email, 
                                                   start_date, 
                                                   fundorg, 
                                                   nick_name, 
                                                   fund_org, 
                                                   fund_org_proj)
    headers     = {'Host': httphost,
                   'Accept':'application/xml',
                   'Content-Type':'application/xml',
                   'Content-Length':str(len(xml_form))}
    request     = "/REST/Project"

    authentic_request   = utils.authenticate_request(request)
    response_dictionary = conn.request('POST',authentic_request,xml_form,headers)
    project_location    = response_dictionary['location']  
    prj_id              = utils.find_experiment_id(project_location)
    return prj_id  

#
# NEESHUB SPECIFIC POSTING FUNCTIONS
#
def post_experiment(project_id, title, description, start_date, experiment_num = ''):
    """This uses the webservices abstraction of httplib in the interface folder
    to post an experiment to NEES
    Args:
        project_id: NEEShub Project Specific IDs
        title: What you want the Experiment Title to be.
        description: How you'd like to describe it.
        start_date: start date
        (experiment_num): Chose experiment number 
            (RECOMMNDED TO LEAVE BLANK!)
    Returns:
        string that is the experiment id for the created experiment."""
    #Generate form for Experiment Name specification.
    name_form       = utils.generate_experiment_name_xml(experiment_num)
    
    #Fill out the XML content form.
    content         = """<Experiment viewable="MEMBERS" type="Structured" >
                            """+name_form+"""
                            <title>"""+title+"""</title>
                            <ExperimentDomain id="1" />
                            <status>private</status>
                            <description>"""+description+"""</description>
                            <startDate>"""+start_date+"""</startDate>
                         </Experiment>"""

    #Fill out the http header dictionary.
    headers        = {'Host': httphost,
                      'Accept': 'application/xml',
                      'Content-Type': 'application/xml',
                      'Content-Length': str(len( content ))  }  
    
    #Generate NEES specific request path.
    request        = "%s%s/Experiment" % (neeshub_project_path, project_id)

    authenticated_request   = utils.authenticate_request(request)
    response_dictionary     = conn.request("POST",authenticated_request, content, headers) 
    triallocation           = response_dictionary['location']  
    exp_id                  = utils.find_experiment_id(triallocation)
    return exp_id    
    

def post_trial(project_id, experiment_id, trialtitle, description, trial_num = ''):      
    '''This uses the abstracted http layer in the interface folder to
    communicate with the NEEShub to post a trial.
    Args:
        project_id: NEEShub Project Specific IDs
        trialtitle: desired title for Trial
        description: desired description. 
            RECOMMENDED: Include entries like "evid: EVTID#", 
            "ml: MAGNITUDE", "dist: Distance from Source"
    Returns:
        string with Trial ID number. '''

    #Generate form for Trial name is specified.
    name_form      = utils.generate_trial_name_xml(trial_num)

    #Fill out the XML content form.
    content        = """                                                   
                    <Trial curationStatus="Uncurated" >
                        """+name_form+"""
                        <title>"""+trialtitle+"""</title>
                        <description>"""+description+"""</description>
                        <status>private</status>
                    </Trial>"""
    
    #Fill out the http header dictionary.
    headers        = {'Host': httphost,
                      'Accept': 'application/xml',
                      'Content-Type': 'application/xml',
                      'Content-Length': str(len( content ))  }  
    #Generate NEES specific request path.
    request        = "%s%s/Experiment/%s/Trial" % (neeshub_project_path, 
                                                   project_id, 
                                                   experiment_id)
    
    #Add authentication to NEES Specific request path and execute post.
    authenticated_request   = utils.authenticate_request(request)
    response_dictionary     = conn.request("POST",authenticated_request, content, headers) 
    triallocation           = response_dictionary['location']  
    trial_id                = utils.find_trial_id(triallocation)
    return trial_id


def post_rep(project_id, experiment_id, trial_id):       
    '''This creates a repetition within a Trial
    Args:
        project_id: NEEShub Project Specific IDs
        experiment_id: NEEShub experiment ID inside Project.
        trial_id: NEEShub trial ID inside Experiment.
    Returns:
        string with Repetition ID.
    '''

    #Fill out XML content form.
    content         = """
                        <Repetition curationStatus="Uncurated" >
                            <startDate></startDate>
                            <endDate></endDate>
                        </Repetition>"""
    
    #Fill out http headers.
    headers         = {'Host': httphost,
                       'Accept': 'application/xml',
                       'Content-Type': 'application/xml',
                       'Content-Length': str(len( content ))  }  
    
    #Generate NEES specific request path.
    request_path    = "%s%s/Experiment/%s/Trial/%s/Repetition" % (neeshub_project_path,
                                                                  project_id, 
                                                                  experiment_id, 
                                                                  trial_id)
    #Add authentication to request path and execute post.
    authentic_request   = utils.authenticate_request(request_path)
    response_dictionary = conn.request("POST",authentic_request, content, headers)
    rep_location    = response_dictionary['location'] 
    rep_id          = utils.find_repetition_id(rep_location)
    return rep_id

def post_full_trial(project_id,experiment_id, trialtitle, description):
    '''Creates a Trial with a Repetition folder inside an experiment. 
    Args:
        project_id: NEEShub Project Specific IDs
        experiment_id: NEEShub experiment ID inside Project.
        trial_id: NEEShub trial ID inside Experiment.
        description: Trial Description.
            RECOMMENDED: Include entries like "evid: EVTID#", 
            "ml: MAGNITUDE", "dist: Distance from Source"            
    Returns:
        tuple of strings with Trial ID and Repetition ID.'''
    trialid         = post_trial(project_id, experiment_id, trialtitle, description)
    repid           = post_rep(project_id, experiment_id, trialid)
    print "Created Repetition: "+repid+" inside Trial: "+trialid
    return trialid, repid
    
def multipart_post(filename, 
                   nees_path_id, 
                   expnum, 
                   trialnum, 
                   rep_num, 
                   datafolder, 
                   request_path = http_file_path, 
                   threading = threading_on,
                   verbose = False):
    '''This is technically an upload post. It assumes that there has already been an FTP file uploaded
    to the NEEShub and is simply waiting assignment. This post will be the assignment.
    Args:
        filename: name of the file you wish to upload.
        nees_path_id: string with the format "NEES-YEAR-PRJID#.groups" This is NEEShub specified..
            EXAMPLE: NEES-2007-0353.groups
        expnum: Experiment Number
        rep_num: Repetition Number
        trialnum: Trial Number
        datafolder: Folder where you wish to upload files within a Repetition.
        (request_path): HTTP Request Parameter, where the post is being made on the HTTP server.
        (threading): When True, it will create a new Thread for every post being made.
        (verbose): When True'''
    xml_sheet           = multipart_http.generate_file_xml(filename, 
                                                           nees_path_id, 
                                                           expnum, 
                                                           trialnum, 
                                                           rep_num, 
                                                           datafolder)
    content_type, body  = multipart_http.encode_multipart_formdata(xml_sheet, 
                                                                   filename, 
                                                                   utils.hub_username, 
                                                                   utils.hub_password)


    headers         = { 
                       'Host'          : httphost,
                       'Content-Type'  : content_type,
                       'Content-Length': str(len(body))
                       }


    authentic_request   = utils.authenticate_request(request_path) 

    # If post is in threading mode, creates a separate thread that executes the post.
    if threading == True:
        threading_request = threading_http.requestThread('POST',authentic_request, body, headers, filename)
        threading_request.start()
    
    # If post is in non-threading mode, this creates a thread
    if threading == False:
        response_dictionary = conn.request('POST',authentic_request, body, headers)
        post_location       = response_dictionary['location']
        post_data           = response_dictionary['data']
        post_status         = response_dictionary['status']
        message              = "%s posted to %s. Status: %s. Reply: %s" % (filename,
                                                                           post_location, 
                                                                           post_status, 
                                                                           post_data)
        nees_logging.append_log(neeshub_log_filename, message)
        return post_status, post_data, post_location

def multipart_post_generic(filename, nees_path_id, expnum, trialnum, selector = http_file_path, threading=False, verbose = False):
    '''This is technically an upload post. It assumes that there has already been an FTP file uploaded
    to the NEEShub and is simply waiting assignment. This post will be the assignment.
    Args:
        filename: name of the file you wish to upload.
        nees_path_id: string with the format "NEES-YEAR-PRJID#.groups" This is NEEShub specified..
            EXAMPLE: NEES-2007-0353.groups
        expnum: Experiment Number
        trialnum: Trial Number
        (selector): HTTP Request Parameter, where the post is being made on the HTTP server.
        (threading): When True, it will create a new Thread for every post being made.
        (verbose): When True'''
    full_filename       = filename
    xml_sheet           = multipart_http.generate_report_xml(full_filename, nees_path_id, expnum, trialnum)
    content_type, body  = multipart_http.encode_multipart_formdata(xml_sheet, full_filename, utils.hub_username, utils.hub_password)


    headers         = { 
                       'Host'          : httphost,
                       'Content-Type'  : content_type,
                       'Content-Length': str(len(body))
                       }


    authentic_request = utils.authenticate_request(selector)

    if threading == True:
        threading_request = threading_http.requestThread('POST',authentic_request, body, headers)
        threading_request.start()

    if threading == False:
        response_dictionary = conn.request('POST',authentic_request, body, headers)
        post_location       = response_dictionary['location']
        post_data           = response_dictionary['data']
        post_status         = response_dictionary['status']
        return post_status, post_data, post_location

#
#NEEShub SPECIFIC DELETE FUNCTIONS
#

def delete_trial(project_id, experiment_id, trial_id):
    '''Allows you to delete Trial Locations.
    Args:
        project_id: NEEShub project ID.
        experiment_id: NEEShub Experiment ID within Project.
        trial_id: NEEShub Trial ID within Experiment.
    Returns:
        integer HTTP status of said request.'''
    
    request    = "%s%s/Experiment/%s/Trial/%s" % (neeshub_project_path,
                                                             project_id, 
                                                             experiment_id, 
                                                             trial_id)
    authentic_request    = utils.authenticate_request(request)
    response_dictionary  = conn.request("DELETE", authentic_request)
    delete_status        = response_dictionary['status']
    return delete_status

def delete_experiment(project_id, experiment_id):
    '''Allows you to delete entire Experiments.
    Args:
        project_id: NEEShub project ID.
        experiment_id: NEEShub Experiment ID within Project.
    Returns:
        integer HTTP status of said request.'''
    #CONFIRM THAT DELETION IS OKAY
    sure = raw_input("Are you SURE you want to DELETE experiment %s, Y/N?" % (experiment_id,))
    sure = sure.lower()

    #DELETION OKAY? SWEET, DO IT.    
    if sure == "y" or "yes":
        request    = "%s%s/Experiment/%s" % (neeshub_project_path,
                                             project_id, 
                                             experiment_id)
        authentic_request    = utils.authenticate_request(request)
        response_dictionary  = conn.request("DELETE", authentic_request)
        delete_status        = response_dictionary['status']
        return delete_status    