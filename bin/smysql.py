import time
import sys
from operator import itemgetter
from config import *
import utils
import mysql.mysql as mysql

conn    = mysql.mySQL(mysql_server, mysql_dbname)


#----------------------------------------------------------------------------------------------------------------------------------------------------------------
# II. High-Level functions   
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
def retrieve_event_description(start_time='', end_time='', ml = mySQL_minimum_magnitude, list_of_sites = None, evid = '', site_evt = ''):
    '''This module will send an execute command to the mySQL server that is equivalent of "select * from lookup
    where parameters = true". Returns a list of tuples where the information is organized in the following order seen
    in the config.py file. 
    start_time and end_time must be entered in epoch time.
    list_of_sites must be a list in the format of ['1', '2', '3']'''
    # If there are no time constraints, this allows to envelop all time.
    if start_time == '':
        start_time = '0'
    if end_time == '':
        end_time = time.time()
    
    # Generate Conditional Selection.    
    select_command          = "select %s from %s" % (mySQL_lookup_order, mySQL_description_table)
    condition_command       = " where time > '%s' and time < '%s' and ml > '%s'" % (start_time, end_time, ml)

    # Pick specific event if asked.
    if evid != '':
        condition_command   += " and evid = '%s'" % (evid,)
    elif site_evt != '':
        condition_command   += " and siteEvt = '%s'" % (site_evt,)
    site_select_command     = utils.generate_site_description_string(list_of_sites)
    mySQLcommand            = select_command + condition_command + site_select_command                                                                         
    
    # Retrieve event description information.
    desclist = conn.request(mySQLcommand)
    sorted_desclist = sorted(desclist, key=itemgetter('time'))                     
    return sorted_desclist

def retrieve_file_location( siteEvt, strlist_of_sites =None):
    '''This function will be used to look at specific site events and where the files that the events are using are located.
    Designed to be used in a "For loop" that uses the output of retrieve_event_description[#]["siteEvt"] output. The "strlist_of_sites"
    allows the user to only ask the trace table to only find the sites they are looking for so that they do not mix up Experiments.
    Returns a list of files that are associated with the siteEvt and list of sites allowed.'''
    site_restriction    = utils.generate_station_description_string(strlist_of_sites)
    mySQLcommand        = "select %s, %s, %s, %s, %s, %s from %s where siteEvt='%s'" % (cfg_fl_dfile, cfg_fl_calib, cfg_fl_segtype, cfg_fl_net, cfg_fl_sta, cfg_fl_chan, mySQL_file_table, siteEvt) + site_restriction
    filelist = conn.request(mySQLcommand)
    return filelist

def retrieve_channel_position( pubChan, event_time):
    '''This module uses information obtained from the trace table of an individual event in order to look up the specifics
    relating to the instrument and channel located under the channsm.sel table. pubChan should just be a string entry reading something like
    "NP_5210_HDD_60" . This can be created from the dictionary response of mySQL trace table request by adding together the "net","sta",
    and "chan" keys of the dictionary with a separator of "_".'''
    time_condition          = " and ontime<'%s' and offtime>'%s'" % (event_time, event_time) 
    mySQLcommand            = "select %s, %s, %s, %s from channel where pubChan ='%s'" % (cfg_chan_dpth, cfg_chan_noffset, cfg_chan_eoffset, cfg_chan_pchan, pubChan, )
    positionlist = conn.request(mySQLcommand+time_condition)
    if len(positionlist)==1:
        return positionlist
    else:
        print "More than one result matching query or None."
        
        
def retrieve_data_folder():
    '''Finds where data is found on the tremor based on what is kept in the mySQL ddir table.'''
    mySQLcommand            = 'select constructor from ddir where ddirId = 1'
    location_dicts          = conn.request(mySQLcommand)
    location_string         = location_dicts[0]['constructor']
    end_loc_index           = location_string.find("%04d/%03d")
    start_loc_index         = location_string.find("'") + 1
    default_data_folder     = location_string[start_loc_index:end_loc_index]
    return default_data_folder 

