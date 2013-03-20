#NEES@UCSB, VAL GORBUNOV
'''This module is designed to create NEES@UCSB specific report files that provide calibration information for 
UCSB's Earthquake data.'''

import datetime
import utils
import smysql
from config import *



def create_report(filepath, event_data_dict, evt_type = 'Earthquake', filename = 'report.csv'):
    '''This function starts the report making process. Populates the general event information, giving Event Id,
    time of event, magnitude, distance and depth, or the dictionary that the ucsbsql_interface module that creates.
    WARNING: This will delete existing report.csv files located in the filepath.'''
    mdd = event_data_dict
    filepath    = utils.close_folder_path(filepath)
    with open(filepath+filename,'w') as report:
        time_now        = str(datetime.datetime.utcnow())
        epoch_time      = mdd[cfg_evt_time]
        event_time      = str(datetime.datetime.fromtimestamp(epoch_time).strftime(default_time_format))
        event_ml        = str(float(mdd[cfg_evt_ml])/100.00)
        event_id        = str(mdd[cfg_evt_evid])
        event_distance  = str(mdd[cfg_evt_dist])
        event_depth     = str(mdd[cfg_evt_depth])
        
        report.write('NEES@UCSB Data Request on ' +time_now+'\n\n')
        report.write('NOTE: miniseed files are never calibrated\n\n')
        report.write('%s::,\n' % (evt_type,)) 
        report.write('Evid:,Time:,Mag:,Dist.(m):,Depth(m):\n')
        report.write('%s,%s,%s,%s,%s\n\n' % (event_id,event_time,event_ml,event_distance,event_depth))
        report.write('CALIBRATION IN PHYSICAL UNITS PER COUNT. Multiply counts by calibration value to get physical measurement.\n\n')
        report.write('STA_CHAN_LOC, Sensor Type, Calib, Cal Units, Depth(m),N_off(m), E_off(m)\n')
        
def append_report(filepath, sensor_data_dict, channel_data_dict, filename = 'report.csv'):
    '''This function will be run once for every file that is moved over from the data directory into the local NEEShub directory.
    Does not delete existing report.csv. Only appends it.'''
    sdd         = sensor_data_dict
    cdd         = channel_data_dict
    filepath    = utils.close_folder_path(filepath)
    with open(filepath + filename,'a') as report:
        sensor_type     = sdd[cfg_fl_segtype]
        calib           = sdd[cfg_fl_calib]
        sta_chan_loc    = sdd[cfg_fl_dfile]
        depth           = cdd[cfg_chan_dpth]
        n_off           = cdd[cfg_chan_noffset]
        e_off           = cdd[cfg_chan_eoffset]
        cal_units       = mySQL_calibdef[sensor_type]

        report.write('%s,%s,%s,%s,%s,%s,%s\n' % (sta_chan_loc, sensor_type, calib, cal_units, depth, n_off, e_off))
        

def append_report_if_valid(filepath, sensor_data_dict, channel_data_dicts, filename = 'report.csv'):  
    '''Since the channel table in the mysql database is a somewhat manual channel this allows
    us to create a report.csv while bypassing secondary information and just including the Calibs.'''
    
    #If channel table exists, proceed as normal and create line in report.csv with channel info.
    if channel_data_dicts != None: 
        channel_data_dict = utils.dict_frm_singular_list(channel_data_dicts)
        append_report(filepath, sensor_data_dict, channel_data_dict, filename)
    
    #Otherwise only use information from the trace table, and note the absence of channel data.
    else:
        channel_data_dict                    = {}
        channel_data_dict[cfg_chan_dpth]     = 'N/A'
        channel_data_dict[cfg_chan_noffset]  = 'N/A'
        channel_data_dict[cfg_chan_eoffset]  = 'N/A'
        data_filename                        = sensor_data_dict[cfg_fl_dfile]
        append_report(filepath, sensor_data_dict, channel_data_dict, filename)       

        
#
# EVENT BASED REPORT GENERATION
#        
        
def generate_evid_report(filepath, event_id, exp_num, evt_type = 'Earthquake', filename = 'report.csv'):
    '''Creates report based on mySQL database in the requested folder.
    Args:
        filepath: Folder path where you want a report.csv created.
        event_id: Event ID of the requested event.
        exp_num: Experiment Number of the event
    '''
    site_list    = mySQL_sitedef[exp_num]
    station_list = mySQL_stadef[exp_num]
    event_dicts  = smysql.retrieve_event_description(list_of_sites = site_list, 
                                                   evid = event_id)
    event_dict   = utils.dict_frm_singular_list(event_dicts)
    site_evt     = event_dict[cfg_evt_siteEvt]
    create_report(filepath, event_dict, evt_type, filename)
    
    # Parse through all files to create individual folder lines.
    file_list   = smysql.retrieve_file_location(site_evt, station_list)
    for file_dict in file_list:
        event_time     = event_dict[cfg_evt_time]
        pub_chan       = "%s_%s_%s" % (file_dict[cfg_fl_net],
                                       file_dict[cfg_fl_sta], 
                                       file_dict[cfg_fl_chan])
        channel_dict  = smysql.retrieve_channel_position(pub_chan, event_time)
        append_report_if_valid(filepath, file_dict, channel_dict, filename) 
        
def generate_CSV(filepath, siteEvt, channel_list = 'all', time='', evt_type = 'Earthquake' ):
    '''Generates CSV file with custom number of channels.
    Args:
        filepath: Folder path or filename path. If filepath is entered as folder 
            path report.csv will be used.
        siteEvt: MYSQL database specific siteEVT assigned to the lookup. Enter 0 
            if you want to create report for non-event type database.
        Channel_List: List of channels you wish to display. Can either be a Python List or a
            string list with comma separated values. Leaving blank or "all" uses all channels.
        time: Time of non-event trials, such as SFSI. If siteEvt is specified, this is ignored.
        evt_type: Header event type for report.csv file. Defaulted at "Earthquake"
    '''
    file_parse      = utils.parse_file_path(filepath)
    filename        = file_parse['filename']
    folder_path     = file_parse['folder']
    channel_cond    = utils.parse_channel_list(channel_list)
    
    # If this is a standard event type, proceed normally.    
    if siteEvt != 0:
        event_dicts = smysql.retrieve_event_description(site_evt = siteEvt)
        event_dict  = utils.dict_frm_singular_list(event_dicts)
        create_report(folder_path, event_dict, evt_type, filename)
        file_list   = smysql.retrieve_file_location(siteEvt)
        
        # Look through every file associated with this siteEvt.
        for file_dict in file_list:
            event_time   = event_dict[cfg_evt_time]
            pub_chan     = "%s_%s_%s" % (file_dict[cfg_fl_net],
                                         file_dict[cfg_fl_sta], 
                                         file_dict[cfg_fl_chan])
            
            # Check if we are allowed to use this channel for creation.
            if pub_chan in channel_cond or channel_cond == 'all':
                channel_dict  = smysql.retrieve_channel_position(pub_chan, event_time)
                append_report_if_valid(folder_path, file_dict, channel_dict, filename)

    # None Event report creation begins if the proper key is set.
    elif siteEvt == 0:
        print "VAL YOU NEED TO PROGRAM IN A REPORT CREATION FOR CROSS-HOLES AND SFSI SHAKES"
        
        
    
    
    