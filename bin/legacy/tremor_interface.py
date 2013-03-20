#THIS WILL BE USED TO INTERFACE DIRECTLY WITH THE TREMOR FILE SERVER
import os
import datetime
import caching
import hub_interface as bhi
import ucsbsql_interface as bui
import neesftp_interface as bni
import report
import utils
import nees_logging
import time
from config import *


#-------------------------------------------------------------------------------------------------------------------------------------------
# I. HIGH LEVEL FUNCTIONS            
#-------------------------------------------------------------------------------------------------------------------------------------------

#
# I. A. Trial Placement Procedures
#

def check_cache_place_trials(expnum, start_time, end_time):
    '''Executes default trial structuring while at the same time creating a new cache file to make sure that no'''
    nees_logging.log_current_time(neeshub_log_filename)
    caching.create_hub_cache(expnum)
    place_trials_default(expnum, start_time, end_time)



def place_trials_default(expnum, start_time, end_time, verbose=False):
    '''This is going to be the primary way of moving processed data from it's proper location
    to the PEN tool's subfolder. As long as the data is organized with our standard format where
    the metadata is located on the mysql database, this will handle all the uploading.
    WARNING: Currently this will not realize if you've pointed it to a folder that it already uploaded.'''    
    destination         = experiment_path[expnum]
    current_trial       = utils.find_last_trial(expnum) + 1                      
    neeshub             = bhi.conn
    mysqldb             = bui.conn
    existing_evid_dict  = caching.load_evid_dictionary(expnum)
    event_data_dicts    = mysqldb.retrieve_event_description(start_time, end_time, list_of_sites = mySQL_sitedef[expnum])
    default_folder      = mysqldb.retrieve_data_folder()
    
    # Look at every event in the database between time constraints.
    for event in event_data_dicts:
        site_evt_number      = event[cfg_evt_siteEvt]
        site_evt_time        = event[cfg_evt_time]
        site_event_id        = event[cfg_evt_evid]
        site_event_dist      = event[cfg_evt_dist]
        site_event_ml        = event[cfg_evt_ml]
        file_data_dicts      = mysqldb.retrieve_file_location(site_evt_number,mySQL_stadef[expnum])
        
        # If this event has already been uploaded, report it and skip this event.
        if site_event_id in existing_evid_dict.values():
            nees_logging.log_existing_evid(site_event_id)
            continue
        
        # Don't do anything if there's no data
        if file_data_dicts == []:
            continue
        
        # Generate file structure on NEEShub and local system.
        description          = utils.generate_description(event)
        trialtitle           = datetime.datetime.utcfromtimestamp(site_evt_time).strftime(default_time_format)
        trial_doc_folder     = "%sTrial-%s/Documentation/" % (destination, current_trial)
        report_name          = 'report.csv'
        caching.update_all_cache_dictionaries(expnum, current_trial, site_event_id, site_event_ml, site_event_dist)        
        utils.generate_trial_structure(destination, current_trial)
        report.create_report(trial_doc_folder, event)
        neeshub.post_full_trial(experiment_id[expnum], trialtitle, description, current_trial)
        
        # Find and move every file within an event to the created file structure. 
        move_datafiles(file_data_dicts, event, destination, current_trial, trial_doc_folder, default_folder, expnum)
        upload_and_post_report(expnum, current_trial, trial_doc_folder, report_name)
        
        
        # Move on to next trial for further processing.
        nees_logging.log_goto_nextline(neeshub_log_filename)
        current_trial += 1
        

def move_datafiles(file_data_dicts, 
                   event, 
                   destination, 
                   current_trial, 
                   trial_doc_folder, 
                   default_folder, 
                   expnum):
    '''Moves datafile from mysql-descripted location to file structure.
    file_                   = mySQL-created dictionary that hold data location info.
    event                   = Dictionary containing event information for the event that "file_" belongs to.
    destination             = Location of Experiment file structure as defined by configuration
    current_trial           = Actually is the trial number that is being worked on.
    trial_doc_folder        = Location of Documentation Files for the event. '''
    mysqldb                 = bui.conn
    julian_folder           = datetime.datetime.utcfromtimestamp(event['time']).strftime(data_retrieval_time_format)

    # Upload every file associated with event.
    for file_ in file_data_dicts:
        filename                = file_[cfg_fl_dfile]
        oscommand_source        = "%s%s%s" % (default_folder, julian_folder, filename)
        oscommand_destination   = "%sTrial-%s/Rep-1/" % (destination, current_trial)
        pubChan                 = "%s_%s_%s" % (file_[cfg_fl_net], file_[cfg_fl_sta], file_[cfg_fl_chan])
        channel_data_dict       = mysqldb.retrieve_channel_position(pubChan, event[cfg_evt_time])
        file_extensions         = utils.find_extensions(oscommand_source)            

        report.append_report_if_valid(trial_doc_folder, 
                                      file_, 
                                      channel_data_dict, 
                                      event[cfg_evt_evid])

        utils.copy_file_exts(oscommand_source, 
                             oscommand_destination, 
                             file_extensions)

        upload_and_post(expnum, 
                        current_trial, 
                        oscommand_destination, 
                        filename, 
                        file_extensions)  
    

#
#TODO: THE BELOW ARE TOO MUCH DUPLICATE CODE, I need a generic UPLOAD and MULTI-PART POST that has FILE subroutines.
#


def upload_and_post(expnum, 
                    trial_number, 
                    source_folder, 
                    filename, 
                    extensions, 
                    selector = http_file_path):
    '''This function is designed to be used in the upload process within the move_datafiles function.
    The filename has to be specified without extension, and the extension has to be specified separately.'''
    for extension in extensions:
        
        full_source_folder    = source_folder + cfg_hub_ext_fold[extension] + '/'
        bhi.ftpconn.upload_file(full_source_folder, filename, extension)
        bhi.conn.multipart_post(filename, expnum, trial_number, extension, selector)

        
def upload_and_post_report(expnum, 
                           trial_number, 
                           source_folder, 
                           filename, 
                           selector = http_file_path):
    '''DUPLICATE CODE, SHOULD RESOLVE GENERIC MULTIPART GENERATOR REGARDLESS OF FILETYPE'''
    source_path         = source_folder + filename
    bhi.ftpconn.upload_to_project(filename, source_path)
    bhi.conn.multipart_post_generic(filename, expnum, trial_number, selector)    
    

       
#
# I. B. Update Report Only 
#

def place_reports_only(expnum, start_time, end_time):
    '''Used in the case that the log gives warning that individual channel information was missing. This allows 
    the used to re-create the report.csv files without having to completely re-do the upload process.'''
    destination         = experiment_path[expnum]                    
    mysqldb             = bui.conn
    event_data_dicts    = mysqldb.retrieve_event_description(start_time, end_time, list_of_sites = mySQL_sitedef[expnum])
    default_folder      = mysqldb.retrieve_data_folder() 
    for event in event_data_dicts:    
        site_evt_number      = event[cfg_evt_siteEvt]
        site_event_id        = event[cfg_evt_evid]
        file_data_dicts      = mysqldb.retrieve_file_location(site_evt_number,mySQL_stadef[expnum])
        current_trial        = caching.trial_num_from_evid(expnum, site_event_id)
        trial_doc_folder     = "%sTrial-%s/Documentation/" % (destination, current_trial)
        report.create_report(trial_doc_folder, event)
        create_filereports(file_data_dicts, 
                           event, 
                           destination, 
                           current_trial, 
                           trial_doc_folder, 
                           default_folder) 
                  

def create_filereports(file_data_dicts, event, destination, current_trial, trial_doc_folder, default_folder):
    mysqldb                 = bui.conn    
    for file_ in file_data_dicts:
        pubChan                 = "%s_%s_%s" % (file_[cfg_fl_net], 
                                                file_[cfg_fl_sta], 
                                                file_[cfg_fl_chan])
        channel_data_dict       = mysqldb.retrieve_channel_position(pubChan, 
                                                                    event[cfg_evt_time])
             
        report.append_report_if_valid(trial_doc_folder, 
                                      file_, 
                                      channel_data_dict, 
                                      event[cfg_evt_evid])
   
   
#
# TODO: THIS IS A ONE OFF PROCESSING SYSTEM
# THIS WORKS ON EMILY'S AND TIM'S CODE. WE NEED TO FIND A WAY TO INTEGRATE IT
# INTO A STANDARD SYSTEM. "lengthofstuff=10" IS A BIG NO-NO. THIS IS WAY TO TITLE
# DEPENDENT.
#

def place_trials(filepath, expnum, lengthofstuff=10):
    '''This uses the "utils.find_last_trial" function to analyze the the destination folder for it's
    Trial content. Based on that information, it will take the files from the given "filepath"
    and place them in proper Trial locations into the destination. The third variable,
    'lengthofstuff' is defaulted at 8, and is used to compare whether the events happened
    on the same day, allowing this function to differential between different Trials.
    WARNING: Currently this will not realize if you've pointed it to a folder that it already uploaded.'''
    destination     = experiment_path[expnum]
    previous        = ''                                                                              
    current_trial   = utils.find_last_trial(expnum)
    pathlist        = sorted(os.listdir(filepath))
    neeshub         = bhi.conn                                                                
    
    for f in pathlist:
        if previous != f[0:lengthofstuff]:
            current_trial += 1      
            precommand = "mkdir -p %sTrial-%s/Rep-1/Derived_Data" % (destination,current_trial)
            os.system(precommand)
            trialtitle = utils.get_trial_title(f, expnum)                                              #Gives Julian Date: Year-Day
            description = experiment_description[expnum]
            neeshub.post_full_trial(experiment_id[expnum], trialtitle, description)           
        command = "cp %s/%s %sTrial-%s/Rep-1/Derived_Data" % (filepath,
                                                              f,
                                                              destination,
                                                              current_trial)
        os.system(command)                                                                                              #Places next Trial folder.
        previous = f[0:lengthofstuff]
    return current_trial  

            

#
# DEBUGGING, REMOVE WHEN FINISHED
#



#The following is kept for troubleshooting purposes. This was before using %s formatting in my strings. If those methos fail use the ones below.
def place_trials_no_hub(filepath, expnum, lengthofstuff=8):                       
    '''This uses the "utils.find_last_trial" function to analyze the the destination folder for it's
    Trial content. Based on that information, it will take the files from the given "filepath"
    and place them in proper Trial locations into the destination.
    WARNING: Currently this will not realize if you've pointed it to a folder that it already uploaded.'''
    destination     = experiment_path[expnum]
    previous        = ''
    trialscreated   = 0                                                           
    current_trial   = utils.find_last_trial(destination)
    pathlist        = sorted(os.listdir(filepath))                                            
    
    for f in pathlist:
        if previous != f[0:lengthofstuff]:
            precommand      = "mkdir -p " +destination+"Trial-"+str(current_trial)+"/Rep-1/Derived_Data"
            os.system(precommand)          
        command = "cp "+filepath+"/"+f+" "+destination+"Trial-"+str(current_trial)+"/Rep-1/Derived_Data"
        os.system(command)
        if previous == f[0:lengthofstuff]:                                      
            current_trial   += 1   
            trialscreated   += 1                                                                                                 
        previous = f[0:lengthofstuff]
    return trialscreated       
                    
