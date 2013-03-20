import os
import time
import string
import datetime
import shutil
import nsite.http as http
from config import *


#
# GENERAL UTILITIES
#    

def to_epoch(date):
    '''Converts MM/DD/YYYY formatted date to epoch time.'''
    pattern = '%m/%d/%Y'
    epoch = int(time.mktime(time.strptime(date, pattern)))
    return epoch
    
def is_number(s):
    '''This function is included in order to make the "get_trial_title()" function be able to check different title formats.
    This function is taken from a Stack Overflow post by Daniel Goldberg on Dec 9th, 2008 under the question "How do I
    check if a string is a number in Python?" I take no credit for this function.'''
    try:
        float(s)
        return True
    except ValueError:
        return False


def dict_frm_singular_list(mysql_list):
    '''This retrieves the dict out of a singular list of dicts.'''
    if len(mysql_list)== 1:
        return mysql_list[0]
    else:
        print "error"  #TODO: ADD RAISE: EXCEPTION

def close_folder_path(filepath):
    '''If passed a filepath without an ending of "/", this adds
    to it.'''
    leng  = len(filepath)
    if filepath[leng-1:leng] != '/':
        filepath += '/'
    return filepath    

def parse_file_path(filepath):
    '''Check if filepath is folder or file. File MUST BE .csv'''
    leng     = len(filepath)
    if filepath[leng-4:leng] == '.csv':
        name_index  = filepath.rfind('/')
        if name_index == -1:
            filename    = filepath
            folder_path = ''
        else:
            filename    = filepath[name_index + 1:]
            folder_path = filepath[:name_index + 1]
    elif filepath.rfind('.') != -1:
        print 'WARNING: Only .csv extension allowed.'
    else:
        filename = 'report.csv'
        folder_path = close_folder_path(filepath) 
    return {'filename': filename, 'folder': folder_path}

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

#
# UCSB SYSTEM
#

def parse_channel_list(string_list):
    '''Designed to work with report creation. Takes a list of channels
    and puts them in an actual list if they are already a non-list format. 
    If string_list == "all" it leaves it alone and passes on.
    '''
    if type(string_list) == list or string_list == 'all':
        return string_list
    elif type(string_list) == str:
        new_list = string_list.split(',')
        return new_list

def copy_filetype(source, destination, msd = True, sac = True, ascii = True):
    '''Function created to make the "place trials default" function more legible. 
    Copies data files to location based on filetype.'''
    
    msd_ext     = '.msd'
    sac_ext     = '.sac'
    ascii_ext   = '.txt'
    # Copy any .msd files with filepath of source to the destination folder.
    if os.path.isfile(source + msd_ext) and msd:
        msd_src = '%s%s' % (source, msd_ext)
        msd_dst = "%s%s/" % (destination, cfg_hub_ext_fold[msd_ext])
        shutil.copy(msd_src, msd_dst)

    # Copy any .sac files with filepath of source to the destination folder.
    if os.path.isfile(source + sac_ext) and sac:
        sac_src = '%s%s' % (source, sac_ext)
        sac_dst = "%s%s/" % (destination, cfg_hub_ext_fold[sac_ext])
        shutil.copy(sac_src, sac_dst)                

    # Copy any .txt files with filepath of source to the destination folder.
    if os.path.isfile(source + ascii_ext) and ascii:
        txt_src = '%s%s' % (source, ascii_ext)
        txt_dst = "%s%s/" % (destination, cfg_hub_ext_fold[sac_ext])
        shutil.copy(txt_src, txt_dst) 
        
def generate_ascii(siteEvt, destination, channel, ext_list):
    '''Tries to use Paul's evtFiles script to generate ASCII files
    for each MSD file.
    Args:
        siteEvt: MySQL-described site-event number.
        destination: Folder to where the file will be created.
        channel: Can be a single channel or a list of channels.
        
    '''
    
    
    # Generate evtFiles compatible channel list string.
    if type(channel) == list:
        channels_str = ''
        for i in channel:
            channels_str += i+','
        # Remove the unnecessary last comma.
        channels_str = channels_str[:-1]
    
    # Or keep Channel List the same.       
    else:
        channels_str = channel
    
    if destination[-1] != '/':
        destination += '/'
    destination   += cfg_hub_ext_fold['.txt']
    final_command = 'evtFiles -dir %s -evt %s -asc v1 %s' % (destination,
                                                             siteEvt,
                                                             channels_str)
    
    #Attempt to create an ASCII file and update the list of extensions.
    try:
        try:
            os.mkdir(destination)
        except:
            pass
        os.system(final_command)
        ext_list.append('.txt')
        return ext_list
    except:
        return ext_list
        
def find_extensions(source, msd = True, sac = True, ascii = True):
    ''' Written to find extensions for files found on mySQL database.'''
    
    msd_ext     = '.msd'
    sac_ext     = '.sac'
    ascii_ext   = '.txt'
    ext_list    = []
    if os.path.isfile(source + msd_ext) and msd:
        ext_list.append(msd_ext)

    if os.path.isfile(source + sac_ext) and sac:
        ext_list.append(sac_ext)               
    
    if os.path.isfile(source + ascii_ext) and ascii:
        ext_list.append(ascii_ext)

    return ext_list


def parse_trial_request(trial_str):
    '''Takes list of trials as a string of "X-Y" and creates a list ranged
    between X and Y. Or simply takes a comma separated string of Trials and
    makes them into a list.'''
    if "-" in trial_str:
        ranges      = trial_str.split('-')
        int_list    = range(int(ranges[0]), int(ranges[1])+1)
        trial_list  = []
        for value in int_list:
            trial_list.append(str(value))
    else:
        trial_list  = trial_str.split(",")

    return trial_list


def copy_file_ext(source, destination, ext):
    '''Copies file when its path is given with no extension, 
    and the extension is given separately.'''
    sourcepath      = source + ext
    destpath        = destination + cfg_hub_ext_fold[ext] + '/'
    shutil.copy(sourcepath, destpath) 
    
def copy_file_exts(source, destination, extensions):
    '''Copies file and multiple instances of this extension.'''
    for ext in extensions:
        copy_file_ext(source, destination, ext)
        

def move_files(src, dst, files):
    '''shutil wrapper for moving a file.
    Filename in source and destination in destination.'''
    for file_ in files:
        fullsrc = "%s/%s" % (src, file_)
        fulldst = "%s/%s" % (dst, file_)
        shutil.move(fullsrc, fulldst)
    
def clean_up(dst):
    '''Deletes events.kml and readme.txt files.'''
    to_remove   = ['readme.txt']

    # Attempt to delete. If fails, who cares.
    try:
        for file_ in to_remove:
            del_path  = "%s/%s" % (dst, file_)
            os.remove(del_path)
    except:
        pass
        
def generate_trial_structure(destination, lasttrial):
    '''Function created to make the "place trials default" function more legible. Generates local NEEShub file structure on tremor.'''
    path_to_dir_1       = "%sTrial-%s/Rep-1/Derived_Data"   % (destination, lasttrial)
    path_to_dir_2       = "%sTrial-%s/Rep-1/Corrected_Data" % (destination, lasttrial)
    path_to_dir_3       = "%sTrial-%s/Rep-1/Converted_Data" % (destination, lasttrial)
    path_to_doc_dir     = "%sTrial-%s/Documentation"        % (destination, lasttrial)
    os.makedirs(path_to_doc_dir)
    os.makedirs(path_to_dir_1)
    os.makedirs(path_to_dir_2) 
    os.makedirs(path_to_dir_3)
    
def find_last_trial(expnum):
    '''This function looks inside the "destination" folder and checks the number of folders.
    It uses the number of folders as the Trial Number to start counting down from. It stops once
    it reaches a Trial number that exists within the "destination". This can also tell if there
    are no Trials within the Directory.'''
    
    trial_dict          = http.get_trial_id_dictionary(expnum)
    lasttrial           = len(trial_dict) + 20
    trial_nums          = [i.split('-',1)[1] for i in trial_dict.keys()]
    #Add Zeros to make the strings sort-able.
    for i in range(len(trial_nums)):
        for h in range(5-len(trial_nums[i])):
            trial_nums[i] = '0' + trial_nums[i]

    trial_nums.sort()
    # Find the largest trial number, should be last entry.
    lasttrial           = int(trial_nums[-1])
    return lasttrial

     
#
# HUB_INTERFACE UTILS
#

def generate_description(meta_dictionary):
    '''This is used to generate a description that will be posted onto the NEEShub under each individual experiment.'''
    lookup_list = mySQL_lookup_order.split(', ')
    description = ''
    for entry in lookup_list[2:]:
        if entry == 'ml':
            old_value = meta_dictionary[entry]
            new_value = str(float(old_value)/100.00)
            dictionary_entry = new_value
        elif entry == 'time':
            old_value = meta_dictionary[entry]
            new_value = datetime.datetime.utcfromtimestamp(old_value).strftime('%m-%d-%Y %H:%M:%S')
            dictionary_entry = new_value
        else:
            dictionary_entry = meta_dictionary[entry]    
        description += entry +': ' +str(dictionary_entry)+'\n' 
    return description

def parse_description(keystring, data):
    '''This is used to parse through the description string in get_trial_metadata_dictionaries_partial to find necessary data.'''
    parse_index = data.find('<description>') + len("<description>")
    s_ind = data[parse_index:].find(keystring) + len(keystring) + parse_index
    e_ind = data[s_ind:].find("\n") + s_ind
    result = data[s_ind:e_ind]
    if result == '':
        print "We could not find the %s in the current description format, please review it and and manually input its value." % (keystring,)
        print data
        result = raw_input('Enter the %s>>>' % (keystring,))
    return result

def get_trial_title(filename, expnum):                                            #Add Differentiation between different experiment title formats. 
    '''This function takes a look at the filename and converts the Julian date to a regular Year, Month, Day
    format. Used in place_trials.'''
    filename = "".join(string.split(filename,'_'))                      #These operations simplify the format of the filename.
    filename = "".join(string.split(filename,'-'))
    if is_number(filename[0:7]):
        datemon = datetime.datetime.strptime(filename[0:7], experiment_title_struct[expnum])
        if is_number(filename[7:13]):
            hours = filename[7:9] +':'+ filename[9:11] +':'+ filename[11:13]
        else:
            hours = ''
        title = str(datemon)[0:11] + hours + experiment_title_time[expnum]
        return title
    else:
        print """ERROR: The filename has an unsupported 'date' format. Please verify that the beginning of the filename is in 
        one of the following supported formats. Year-JulianDay,YearJulianDay,Year_JulianDay. To add formats, you must edit 
        the function 'get_trial_title()' under 'tremor_interface.py' in the bin directory."""


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# III. MySQL module auxiliary functions.
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------           
    
def generate_site_description_string(list_of_sites = None):
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

def generate_station_description_string(list_of_sites = None):
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
        
           