# Val Gorbunov, NEES@UCSB
# HOLDS THE PRIMARY MACRO COMMANDS FOR UPLOADING TO NEESHUB
import datetime
import time
import caching
import nsite.nees.nees_logging as nees_logging
import nsite.http as shttp
import smysql
import nsite.nees_upload as snupload
import nsite.nees.ftp as snftp
import utils
import report
from config import *
from nsite.nees.config import *

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
    existing_evid_dict  = caching.load_evid_dictionary(expnum)
    event_data_dicts    = smysql.retrieve_event_description(start_time, end_time, list_of_sites = mySQL_sitedef[expnum])
    default_folder      = smysql.retrieve_data_folder()
    
    # Look at every event in the database between time constraints.
    for event in event_data_dicts:
        site_evt_number      = event[cfg_evt_siteEvt]
        site_evt_time        = event[cfg_evt_time]
        site_event_id        = event[cfg_evt_evid]
        site_event_dist      = event[cfg_evt_dist]
        site_event_ml        = event[cfg_evt_ml]
        file_data_dicts      = smysql.retrieve_file_location(site_evt_number,mySQL_stadef[expnum])
        
        # If this event has already been uploaded, report it and skip this event.
        if site_event_id in existing_evid_dict.values():
            nees_logging.log_existing_evid(site_event_id)
            continue
        
        # Don't do anything if there's no data
        if file_data_dicts == []:
            continue
        
        # Generate file structure on shttp and local system.
        description          = utils.generate_description(event)
        trialtitle           = datetime.datetime.utcfromtimestamp(site_evt_time).strftime(default_time_format)
        trial_doc_folder     = "%sTrial-%s/Documentation/" % (destination, current_trial)    
        report_source        = "%sTrial-%s/Rep-1/%s/" % (destination, current_trial,cfg_hub_ext_fold['.txt'])    
        report_name          = 'report.csv'
        readme_name          = 'readme.pdf'
        events_kml           = 'event.kml'
        utils.generate_trial_structure(destination, current_trial)
        shttp.post_full_trial(shttp.experiment_id_dic[expnum], trialtitle, description, current_trial)
        
        # Find and move every file within an event to the created file structure. 
        move_datafiles(file_data_dicts, event, destination, current_trial, trial_doc_folder, default_folder, expnum)
        utils.move_files(report_source, trial_doc_folder, [report_name, readme_name, events_kml])
        snupload.upload_reportfile(expnum, current_trial, trial_doc_folder, report_name)
        snupload.upload_reportfile(expnum, current_trial, trial_doc_folder, readme_name)
        snupload.upload_reportfile(expnum, current_trial, trial_doc_folder, events_kml)
        utils.clean_up(report_source)
        
        
        # Move on to next trial for further processing after updating cache..
        nees_logging.log_goto_nextline(neeshub_log_filename)
        caching.update_all_cache_dictionaries(expnum, current_trial, site_event_id, site_event_ml, site_event_dist)
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
    julian_folder           = datetime.datetime.utcfromtimestamp(event['time']).strftime(data_retrieval_time_format)
    file_queue_dict         = {}
    pubchan_queue_list      = []
    file_extensions         = ['.msd']
    siteEvt                 = event[cfg_evt_siteEvt]

    # Generate a dictionary Queue fo all information to prepare upload.
    for file_ in file_data_dicts:
        filename                = file_[cfg_fl_dfile]
        oscommand_source        = "%s%s%s" % (default_folder, julian_folder, filename)
        oscommand_destination   = "%sTrial-%s/Rep-1/" % (destination, current_trial)
        pubChan                 = "%s_%s_%s" % (file_[cfg_fl_net], file_[cfg_fl_sta], file_[cfg_fl_chan])
           

        file_queue_dict[filename]   = [oscommand_source,
                                       oscommand_destination,
                                       pubChan]
        pubchan_queue_list.append(pubChan)

    # Generate ASCII and report.csv files for event.        
    file_extensions         = utils.generate_ascii(siteEvt, 
                                                   oscommand_destination, 
                                                   pubchan_queue_list, 
                                                   file_extensions)

    # Copy .msd files to proper directory and upload .msd and .txt files.
    for filename in file_queue_dict.keys():
        oscommand_source        = file_queue_dict[filename][0]
        oscommand_destination   = file_queue_dict[filename][1]
        pubChan                 = file_queue_dict[filename][2]
        
        utils.copy_file_exts(oscommand_source, 
                             oscommand_destination, 
                             ['.msd'])
        
        #TODO: IDIOTICY
        # APPARENTLY AFTER MAKING THE FIRST UPLOAD AND POST I NEED TO WAIT BEFORE ATTEMPTING
        # THE REST, OTHERWISE THREE OF THE FILES WILL FAIL
        # WITH THIS, ALL IS HAPPY AND GOOD 
        if file_data_dicts.index(file_) == 1: # WHAT THE HELL
            time.sleep(5)                     # NO SERIOUSLY, WHY IS THIS OKAY? 
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
        full_filename         = filename + extension
        data_folder           = cfg_hub_ext_fold[extension]
        snupload.upload_datafile(expnum, trial_number, '1', data_folder, source_folder, full_filename, selector)
        
        
def place_reports_only(expnum, start_time, end_time):
    destination         = experiment_path[expnum]                    
    event_data_dicts    = smysql.retrieve_event_description(start_time, end_time, list_of_sites = mySQL_sitedef[expnum])
    default_folder      = smysql.retrieve_data_folder()
    
    # Look at every event in the database between time constraints.
    for event in event_data_dicts:
        site_evt_number      = event[cfg_evt_siteEvt]
        site_event_id        = event[cfg_evt_evid]
        file_data_dicts      = smysql.retrieve_file_location(site_evt_number,mySQL_stadef[expnum])
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
    '''Creates reports without interfacing with the files
    themselves.'''
    for file_ in file_data_dicts:
        pubChan                 = "%s_%s_%s" % (file_[cfg_fl_net], 
                                                file_[cfg_fl_sta], 
                                                file_[cfg_fl_chan])
        channel_data_dict       = smysql.retrieve_channel_position(pubChan, 
                                                                    event[cfg_evt_time])
             
        report.append_report_if_valid(trial_doc_folder, 
                                      file_, 
                                      channel_data_dict, 
                                      event[cfg_evt_evid])
                  
