'''This module exists to primarily interface with UCSB's mySQL database that stores information about seismological 
events recorded by the Earth Research Institute's permanently instrumented field sites.'''

from config import *
from operator import itemgetter
import sys
import MySQLdb
import getpass

#---------------------------------------------------------------------------------------------------------------------------------------------------------
# I. Initialization and Basic Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------

class ucsbSQL(object):
    '''This class instance creates a connection with the UCSB's mySQL interface. ucsbSQL becomes the defined object
    that has functions applied to it in order to perform specific tasks. Tasks such as determining which information to
    apply to each individual trial being uploaded to the NEEShub.'''
    
    def __init__(self, host='fern.nees.ucsb.edu'):
        self.host           = host
        self.con            = None
        self.username       = raw_input('mySQL Username: ')
        self.password       = getpass.getpass()
        self.connect()
        
    def connect(self):
        '''This module is responsible for connecting the ucsbSQL class to the mySQL database. Very basic connection
        that double checks for existing connections.'''
        if self.con is not None:
            self.con.close()
            del self.con
            self.con = None
        self.con = MySQLdb.connect(mySQL_host, self.username, self.password,mySQL_database_name)
        
    def mysql_request(self, request_parameters):
        '''Basic mySQL request command. This basically condenses the process of sending a mySQL
        request with a MySQLdb "cursor" object, and automatically returns the reply to the mySQL
        request.'''
        self.returned_list = []
        with self.con:
            cur = self.con.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(request_parameters)
            rows = cur.fetchall()
            for row in rows:
                self.returned_list.append(row)
        return self.returned_list
        
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
# II. High-Level functions   
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def retrieve_event_description(self, start_time, end_time, ml = mySQL_minimum_magnitude, list_of_sites = None):
        '''This module will send an execute command to the mySQL server that is equivalent of "select * from lookup
        where parameters = true". Returns a list of tuples where the information is organized in the following order seen
        in the config.py file. 
        start_time and end_time must be entered in epoch time.
        list_of_sites must be a list in the format of ['1', '2', '3']'''
        select_command          = "select %s from %s" % (mySQL_lookup_order, mySQL_description_table)
        condition_command       = " where time > '%s' and time < '%s' and ml > '%s'" % (start_time, end_time, ml)
        site_select_command     = self.generate_site_description_string(list_of_sites)
        mySQLcommand            = select_command + condition_command + site_select_command                                                                         
        
        # Retrieve event description information.
        self.desclist = self.mysql_request(mySQLcommand)
        sorted_desclist = sorted(self.desclist, key=itemgetter('time'))                     
        return sorted_desclist
    
    def retrieve_file_location(self, siteEvt, strlist_of_sites):
        '''This function will be used to look at specific site events and where the files that the events are using are located.
        Designed to be used in a "For loop" that uses the output of retrieve_event_description[#]["siteEvt"] output. The "strlist_of_sites"
        allows the user to only ask the trace table to only find the sites they are looking for so that they do not mix up Experiments.
        Returns a list of files that are associated with the siteEvt and list of sites allowed.'''
        site_restriction    = self.generate_station_description_string(strlist_of_sites)
        mySQLcommand        = "select %s, %s, %s, %s, %s, %s from %s where siteEvt='%s'" % (cfg_fl_dfile, cfg_fl_calib, cfg_fl_segtype, cfg_fl_net, cfg_fl_sta, cfg_fl_chan, mySQL_file_table, siteEvt) + site_restriction
        self.filelist = self.mysql_request(mySQLcommand)
        return self.filelist
    
    def retrieve_channel_position(self, pubChan, event_time):
        '''This module uses information obtained from the trace table of an individual event in order to look up the specifics
        relating to the instrument and channel located under the channel table. pubChan should just be a string entry reading something like
        "NP_5210_HDD_60" . This can be created from the dictionary response of mySQL trace table request by adding together the "net","sta",
        and "chan" keys of the dictionary with a separator of "_".'''
        time_condition          = " and ontime<'%s' and offtime>'%s'" % (event_time, event_time) 
        mySQLcommand            = "select %s, %s, %s, %s from channel where pubChan ='%s'" % (cfg_chan_dpth, cfg_chan_noffset, cfg_chan_eoffset, cfg_chan_pchan, pubChan, )
        self.positionlist = self.mysql_request(mySQLcommand+time_condition)
        if len(self.positionlist)==1:
            return self.positionlist
        else:
            print "More than one result matching query or None."
            
            
    def retrieve_data_folder(self):
        '''Finds where data is found on the tremor based on what is kept in the mySQL ddir table.'''
        mySQLcommand            = 'select constructor from ddir where ddirId = 1'
        location_dicts          = self.mysql_request(mySQLcommand)
        location_string         = location_dicts[0]['constructor']
        end_loc_index           = location_string.find("%04d/%03d")
        start_loc_index         = location_string.find("'") + 1
        default_data_folder     = location_string[start_loc_index:end_loc_index]
        return default_data_folder 

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# III. Auxiliary Functions
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------           
        
    def generate_site_description_string(self, list_of_sites = None):
        '''This function exists specifically to generate a mysql-friendly statement that allows to filter the lookup tables based on site.
        Basically if you pass a list ['1','100','101'] into it, the returned string would read " and (site = 1 or site = 100 or site = 101)"'''
        # Initiate the included filtering conditions by starting with an "and".
        if list_of_sites is not None:
            site_select = ' and ('                                                                            
            
            # Create a sequence of "or" conditions for the possible match of "site" variable.
            for site in list_of_sites:
                site_select +=  "site = '%s' or " % (site,)
            select_string = site_select[0:len(site_select)-4] +')'                                   
        
        # If site definition is irrelevant, pass an empty string.
        else:
            select_string = ''
        
        # Returns an additional condition for mySQL filtering.    
        return select_string
    
    def generate_station_description_string(self, list_of_sites = None):
        '''This function exists specifically to generate a mysql-friendly statement that allows to filter the lookup tables based on site.
        Basically if you pass a list ['1','100','101'] into it, the returned string would read " and (site = 1 or site = 100 or site = 101)"'''
        # If there is station name condition, initiate the included filtering conditions by starting with an "and".
        if list_of_sites is not None:
            site_select = ' and ('                                                                            
            
            # Create a sequence of "or" conditions for the possible match of "sta" variable.            
            for site in list_of_sites:
                site_select +=  "sta = '%s' or " % (site,)
            select_string = site_select[0:len(site_select)-4] +')'                                   

        # If there is no station name condition return empty condition.
        else:
            select_string = ''
        
        # Returns additional condition for mySQL filtering.
        return select_string
            
            
conn = ucsbSQL()