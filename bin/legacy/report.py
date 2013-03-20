#NEES@UCSB, VAL GORBUNOV
'''This module is designed to create NEES@UCSB specific report files that provide calibration information for 
UCSB's Earthquake data.'''

import datetime
import nsite.nees.nees_logging as nees_logging
import utils
from config import *



def create_report(filepath, event_data_dict):
    '''This function starts the report making process. Populates the general event information, giving Event Id,
    time of event, magnitude, distance and depth, or the dictionary that the ucsbsql_interface module that creates.
    WARNING: This will delete existing report.csv files located in the filepath.'''
    mdd = event_data_dict
    with open(filepath+'report.csv','w') as report:
        time_now        = str(datetime.datetime.utcnow())
        epoch_time      = mdd[cfg_evt_time]
        event_time      = str(datetime.datetime.fromtimestamp(epoch_time).strftime(default_time_format))
        event_ml        = str(float(mdd[cfg_evt_ml])/100.00)
        event_id        = str(mdd[cfg_evt_evid])
        event_distance  = str(mdd[cfg_evt_dist])
        event_depth     = str(mdd[cfg_evt_depth])
        
        report.write('NEES@UCSB Data Request on ' +time_now+'\n\n')
        report.write('NOTE: miniseed files are never calibrated\n\n')
        report.write('Earthquake::,\n')
        report.write('Evid:,Time:,Mag:,Dist.(m):,Depth(m):\n')
        report.write('%s,%s,%s,%s,%s\n\n' % (event_id,event_time,event_ml,event_distance,event_depth))
        report.write('CALIBRATION IN PHYSICAL UNITS PER COUNT. Multiply counts by calibration value to get physical measurement.\n\n')
        report.write('STA_CHAN_LOC, Sensor Type, Calib, Cal Units, Depth(m),N_off(m), E_off(m)\n')
        
def append_report(filepath, sensor_data_dict, channel_data_dict):
    '''This function will be run once for every file that is moved over from the data directory into the local NEEShub directory.
    Does not delete existing report.csv. Only appends it.'''
    sdd         = sensor_data_dict
    cdd         = channel_data_dict
    
    with open(filepath + 'report.csv','a') as report:
        sensor_type     = sdd[cfg_fl_segtype]
        calib           = sdd[cfg_fl_calib]
        sta_chan_loc    = sdd[cfg_fl_dfile]
        depth           = cdd[cfg_chan_dpth]
        n_off           = cdd[cfg_chan_noffset]
        e_off           = cdd[cfg_chan_eoffset]
        cal_units       = mySQL_calibdef[sensor_type]

        report.write('%s,%s,%s,%s,%s,%s,%s\n' % (sta_chan_loc, sensor_type, calib, cal_units, depth, n_off, e_off))
        

def append_report_if_valid(filepath, sensor_data_dict, channel_data_dicts, evid):  
    '''Since the channel table in the mysql database is a somewhat manual channel this allows
    us to create a report.csv while bypassing secondary information and just including the Calibs.'''
    
    #If channel table exists, proceed as normal and create line in report.csv with channel info.
    if channel_data_dicts != None: 
        channel_data_dict = utils.dict_frm_singular_list(channel_data_dicts)
        append_report(filepath, sensor_data_dict, channel_data_dict)
    
    #Otherwise only use information from the trace table, and note the absence of channel data.
    else:
        channel_data_dict                    = {}
        channel_data_dict[cfg_chan_dpth]     = 'N/A'
        channel_data_dict[cfg_chan_noffset]  = 'N/A'
        channel_data_dict[cfg_chan_eoffset]  = 'N/A'
        data_filename                        = sensor_data_dict[cfg_fl_dfile]
        append_report(filepath, sensor_data_dict, channel_data_dict)       
        nees_logging.log_invalid_report(evid, data_filename)