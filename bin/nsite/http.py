#Adapts the abstracted http layer to our NEEShub-specific interfaces.
#Created by Val Gorbunov for the use of NEES@UCSB
from nees.config import *
import nees.http as nh
import nees.nees_logging as nees_logging


#
# NEESHUB SPECIFIC GET FUNCTIONS
#

def get_experiment_id_dictionary():
    ''' UCSB NEES SPECIFIC function from the http server in nees folder.
    Returns:
        dictionary of Experiment-IDs in the format of
            {'Experiment#':'ID#'...}'''
    response = nh.get_experiment_id_dictionary(sitenees_proj)
    return response

# This variable dictionary used to be updated manually. Now it initiates automatically
# in order to simplify that process.
experiment_id_dic = get_experiment_id_dictionary()    



def get_trial_id_dictionary(experiment_num):
    ''' UCSB NEES SPECIFIC function from the http server in nees folder.
    Args:
        experiment_num: NEEShub Experiment Number.
    Returns:
        dictionary of Trial-IDs in the format of
            {'Trial-#':'ID#'...} 
    """'''
    experiment_id = experiment_id_dic[experiment_num]
    response = nh.get_trial_id_dictionary(sitenees_proj, experiment_id)    
    return response   

def get_trial_metadata_dictionaries_partial(experiment_num, experimentdict):
    ''' UCSB NEES SPECIFIC function from the http server in nees folder.'''
    experiment_id = experiment_id_dic[experiment_num]
    cache_evid_dict, cache_ml_dict, cache_distance_dict = nh.get_trial_metadata_dictionaries_partial(sitenees_proj, 
                                                                                                     experiment_id, 
                                                                                                     experimentdict)
    return cache_evid_dict, cache_ml_dict, cache_distance_dict

def get_trial_metadata_dictionaries(experiment_num):
    """Gets metadata from trial descriptions. 
    WARNING: This requires trial description defines metadata in the
    'datatype: data' format.
    Args:
        experiment_id: NEEShub Experiment ID. Use
            get_experiment_id_dictionary to acquire.
    Returns:
        3-part tuple of dictionaries. Dictionary of event ids, 
        magnitude ids and distance ids. Keys are 'Trial-#'"""
    experiment_id = experiment_id_dic[experiment_num]
    evid_dict, ml_dict, dist_dict = nh.get_trial_metadata_dictionaries(sitenees_proj, experiment_id)
    return evid_dict, ml_dict, dist_dict


#
# NEESHUB SPECIFIC POSTING FUNCTIONS
#

def post_experiment(title, description, start_date, experiment_num = ''):
    """"This uses the webservices abstraction of httplib in the interface folder
    to post an experiment to NEES
    Args:
        title: What you want the Experiment Title to be.
        description: How you'd like to describe it.
        start_date: start date
        (experiment_num): Chose experiment number 
            (RECOMMNDED TO LEAVE BLANK!)
    Returns:
        string that is the experiment id for the created experiment."""
    experiment_id     = nh.post_experiment(sitenees_proj, title, description, start_date, experiment_num = '')
    return experiment_id
    
def post_trial(experiment_id, trialtitle, description, trial_num = ''):      
    '''This uses the abstracted http layer in the interface folder to
    communicate with the NEEShub to post a trial.
    Args:
        trialtitle: desired title for Trial
        description: desired description. 
            RECOMMENDED: Include entries like "evid: EVTID#", 
            "ml: MAGNITUDE", "dist: Distance from Source"
    Returns:
        string with Trial ID number. '''

    trial_id                = nh.post_trial(sitenees_proj, experiment_id, trialtitle, description)
    return trial_id

def post_rep(experiment_id, trial_id):       
    """This creates a repetition within a Trial
    Args:
        experiment_id: NEEShub experiment ID inside Project.
        trial_id: NEEShub trial ID inside Experiment.
    Returns:
        string with Repetition ID."""
    rep_id                  = nh.post_rep(sitenees_proj, experiment_id, trial_id)
    return rep_id

def post_full_trial(experiment_id, trialtitle, description, trial_num = ''):
    '''Creates a Trial with a Repetition folder inside an experiment. 
    Args:
        experiment_id: NEEShub experiment ID inside Project.
        trial_id: NEEShub trial ID inside Experiment.
        description: Trial Description.
            RECOMMENDED: Include entries like "evid: EVTID#", 
            "ml: MAGNITUDE", "dist: Distance from Source"            
    Returns:
        tuple of strings with Trial ID and Repetition ID.'''
    trialid, repid  = nh.post_full_trial(sitenees_proj, experiment_id, trialtitle, description)
    nees_logging.log_trial_creation(trial_num, experiment_id, trialid, repid)
    return trialid, repid
    
def multipart_post(filename, expnum, trialnum, rep_num,  datafolder, request_path = http_file_path, verb = False):
    '''This is technically an upload post. It assumes that there has already been an FTP file uploaded
    to the NEEShub and is simply waiting assignment. This post will be the assignment.
    Args:
        filename: name of the file you wish to upload.
        expnum: Experiment Number
        rep_num: Repetition Number
        trialnum: Trial Number
        datafolder: Folder where you wish to upload files within a Repetition.
        (request_path): HTTP Request Parameter, where the post is being made on the HTTP server.
        (threading): When True, it will create a new Thread for every post being made.
        (verb): When True show progress. NOTE YET IMPLEMENETED.'''
    post_status, post_data, post_location = nh.multipart_post(filename, 
                                                              nees_path_id, 
                                                              expnum, 
                                                              trialnum, 
                                                              rep_num, 
                                                              datafolder, 
                                                              request_path,  
                                                              verbose = verb)
    return post_status, post_data, post_location


#
# SITE NEESHUB SPECIFIC DELETE FUNCTIONS
#

def delete_experiment(experiment_num):
    '''Deletes site specific experiment.
    Args:
        experiment_num: Experiment number that is to be deleted within the project.
    Returns:
        integer, HTTP status response.'''
    experiment_id           = experiment_id_dic[experiment_num]
    del_status              = nh.delete_experiment(sitenees_proj, experiment_id)
    return del_status

def delete_trial(experiment_num, trial_number):
    '''Deletes site specific experiment.
    Args:
        experiment_num: Experiment number for the Trial to be deleted..
        trial_number: Trial number that is to be deleted within the experiment.
    Returns
        integer, HTTP status response.''' 
    experiment_id           = experiment_id_dic[experiment_num]
    trial_dict              = get_trial_id_dictionary(experiment_num)
    trial_key               = 'Trial-%s' % (trial_number,)
    trial_id                = trial_dict[trial_key]
    del_status              = nh.delete_trial(sitenees_proj, experiment_id, trial_id)
    return del_status   
