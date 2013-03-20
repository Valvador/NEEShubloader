import os
import string
import datetime
import shutil
from config import *


#
# GENERAL UTILITIES
#    
    
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
# TREMOR UTILITIES
#

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
    destination         = experiment_path[expnum]
    dest_directory      = sorted(os.listdir(destination))
    lasttrial           = len(dest_directory)
    
    # Find the largest trial number, counting down from the number of folders in directory.
    while not ("Trial-"+str(lasttrial)) in dest_directory:                      
        if lasttrial == 0:
            print "There are no trials in %s" % (destination,)
            break
        lasttrial = lasttrial - 1    
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


    