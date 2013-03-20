# VAL GORBUNOV DEC 12, 2012 
# NEES@UCSB
import os
from datetime import datetime
from config import *

#
# I. LOW LEVEL BASIC-COMMANDS
#

def create_log(filename, message):
    '''Simple command that overwrites existing files and creates one if it doesn't
    exist.'''
    log_dir         = find_log_dir()
    filepath        = '%s/%s' % (log_dir, filename)
    message         += '\n' 
    with open(filepath, 'w') as log_file:
        log_file.write(message)

def append_log(filename, message):
    '''Simple command that doesn't overwrite existing file, but adds to the end.
    Creates file if it doesn't exist.'''
    log_dir         = find_log_dir()
    filepath        = '%s/%s' % (log_dir, filename)
    message         += '\n'                      
    with open(filepath, 'a') as log_file:
        log_file.write(message)
        
def append_log_sameline(filename, message):
    '''Simple command that doesn't overwrite existing file, but adds to the end.
    Creates file if it doesn't exist.'''
    log_dir         = find_log_dir()
    filepath        = '%s/%s' % (log_dir, filename)
                      
    with open(filepath, 'a') as log_file:
        log_file.write(message)        

#
# II. PRIMARY FUNCTIONS
#
    
def log_current_time(filename):
    '''Use this function at the beginning of every event that is being logged. This
    will print a line that gives a timestamp based on UTC time.'''
    #current_utc_time stores time to the second ([:-7] makes sure of this).
    current_utc_time         = str(datetime.utcnow())[:-7]
    current_time_log_entry   = '==================%s UTC==================' % (current_utc_time,)
    append_log(filename, current_time_log_entry)
    
def log_trial_creation(trial_number, experiment_id, trial_id, rep_id):
    '''Makes log entry to the NEEShub.log file. Instance used in hub_interface's place_full_trial function.'''
    filename        = neeshub_log_filename
    message         = "#INFO: CREATING Trial #%s created at %sExperiment/%s/Trial/%s/Repetition/%s  SOURCE: hub_interface.place_full_trial" % (trial_number, neeshub_project_path, experiment_id, trial_id, rep_id)
    
    append_log(filename, message)
    
def log_cache_invalid_cache_variables(trial_str, evid, ml, dist):
    '''Makes log entry to NEEShub.log file. Instance used in hub_interface's get_trial_metadata_dictionaries_partial
    function.'''
    if "INVALID" in [evid, ml, dist]:
        filename        = neeshub_log_filename
    
        # Append Log if there is an instance of "Invalid" in evid cache.
        if evid == "INVALID":
            message     = "#WARNING: %s: INVALID value in 'evid' cache." % (trial_str,)
            append_log(filename, message)
    
        # Append Log if there is an instance of "Invalid" in ml cache.
        if ml   == "INVALID":
            message     = "#WARNING: %s: INVALID value in 'ml' cache." % (trial_str,)
            append_log(filename, message)
    
        # Append Log if there is an instance of "Invalid" in dist cache.
        if dist == "INVALID":
            message     = "#WARNING: %s: INVALID value in 'dist' cache." % (trial_str,)
            append_log(filename, message)
        
def log_existing_evid(evid):
    '''Used in tremor_interface's cache check during place_trial_default.'''
    filename        = neeshub_log_filename
    message         = "#WARNING: evid %s already exists, skipping. May want to investigate." % (evid,)
    append_log(filename, message)
    

def log_invalid_report(evid, filename):
    '''Used in instances that information for creating a report.csv is not available.'''
    filename        = neeshub_log_filename
    message         = "#WARN: evid %s,  %s " % (evid, filename)
    append_log(filename, message)#


def log_goto_nextline(filename):
    '''Used after invalid report to go to next line to avoid multiple lines for error messages.'''
    filename        = neeshub_log_filename
    message         = '#INFO: DONE'
    append_log(filename, message)
    
#
# LOGGING UTILITIES
#

def find_log_dir():
    '''This looks for the "cache" folder under the NEEShubloader. If it exists, it
    simply returns it's location on the system. If it doesn't exist it also creates the
    directory.'''
    cwd             = os.path.abspath(__file__)
    path_index      = cwd.find('NEEShubloader')
    log_dir         = '%sNEEShubloader/bin/logs' % (cwd[:path_index],)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

        