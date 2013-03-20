#Created by Val Gorbunov for the use of NEES@UCSB

from config import *
import nsite.http as shttp 
import nsite.mysql as smysql
import pickle
import os

#------------------------------------------------------------------------------------------------------------------------------------------
# I. BASIC CACHE FUNCTIONS
#------------------------------------------------------------------------------------------------------------------------------------------

def create_new_cache(filepath, cache_dictionary):
    '''This function will be run to create a new Cache on system in order to pre redundant Trials. Every time the uploader
    software is run, it will create a new Cache. Any subsequent commands after the first initialization will only UPDATE the cache.'''
    new_cache           = open(filepath,'w')
    pickle.dump(cache_dictionary, new_cache)
    new_cache.close()
    
def load_existing_cache(filepath):
    '''This function imports existing .pkl cache'''
    imported_dictionary = {}
    if os.path.isfile(filepath):
        existing_cache      = open (filepath, 'rb')
        imported_dictionary = pickle.load(existing_cache)
        existing_cache.close()    
    return imported_dictionary

def update_existing_cache(filepath, new_dictionary_entry):
    '''This function will be run when dealing with an existing cache that is already trusted.'''
    existing_cache      = open(filepath, 'rb')
    imported_dictionary = pickle.load(existing_cache)
    existing_cache.close()
    imported_dictionary.update(new_dictionary_entry)
    
    existing_cache      = open(filepath, 'wb')
    pickle.dump(imported_dictionary, existing_cache)
    existing_cache.close()
    
#------------------------------------------------------------------------------------------------------------------------------------------
# II. PRIMARY (HIGHER LEVEL) CACHE FUNCTIONS
#------------------------------------------------------------------------------------------------------------------------------------------

def create_hub_cache(expnum):
    '''Looks at the NEEShub and creates .pkl files that contain the dictionary information about
    the NEEShub experiments.'''    
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)
    filepath_evid                   = cache_dir + pre_file + '_evid.pkl'
    filepath_ml                     = cache_dir + pre_file + '_ml.pkl'
    filepath_dist                   = cache_dir + pre_file + '_dist.pkl'
    
    evid_dict, ml_dict, dist_dict   = shttp.get_trial_metadata_dictionaries(expnum)
    create_new_cache(filepath_evid, evid_dict)
    create_new_cache(filepath_ml, ml_dict)
    create_new_cache(filepath_dist, dist_dict)


def load_evid_dictionary(expnum):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_evid                   = cache_dir + pre_file + '_evid.pkl'
    evid_dictionary = load_existing_cache(filepath_evid)
    return evid_dictionary

def load_ml_dictionary(expnum):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_ml                   = cache_dir + pre_file + '_ml.pkl'
    ml_dictionary = load_existing_cache(filepath_ml)
    return ml_dictionary    

def load_dist_dictionary(expnum):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_dist                   = cache_dir + pre_file + '_dist.pkl'
    dist_dictionary = load_existing_cache(filepath_dist)
    return dist_dictionary
    

def update_evid_dictionary(expnum, trial_number, evid):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_evid                   = cache_dir + pre_file + '_evid.pkl'
    cache_key                       = "Trial-%s" % (trial_number,)
    dict_to_paste                   = {cache_key:long(evid)}
    update_existing_cache(filepath_evid, dict_to_paste)
    


def update_ml_dictionary(expnum, trial_number, ml):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_evid                   = cache_dir + pre_file + '_ml.pkl'
    cache_key                       = "Trial-%s" % (trial_number,)
    dict_to_paste                   = {cache_key:ml}
    update_existing_cache(filepath_evid, dict_to_paste)



def update_dist_dictionary(expnum, trial_number, dist):
    ''''''
    cache_dir                       = find_cache_dir()
    pre_file                        = '/exp%s' % (expnum,)    
    filepath_evid                   = cache_dir + pre_file + '_dist.pkl'
    cache_key                       = "Trial-%s" % (trial_number,)
    dict_to_paste                   = {cache_key:dist}
    update_existing_cache(filepath_evid, dict_to_paste)
    
def update_all_cache_dictionaries(expnum, trial_number, evid, ml, dist):
    '''Combines all update cache functions into one simple cobined command.'''
    update_evid_dictionary(expnum, trial_number, evid)
    update_ml_dictionary(expnum, trial_number, evid)
    update_dist_dictionary(expnum, trial_number, evid)


#TODO: REMEMBER TO CREATE A FUNCTION THAT COMPARES THE .PKL FILES TO THE COMPLETE MYSQL HISTORY FOR INDIVIDUAL STATION.



#-------------------------------------------------------------------------------------------------------------------------------------------
# III. CACHE SYSTEM TOOLS
#-------------------------------------------------------------------------------------------------------------------------------------------
    

def find_cache_dir():
    '''This looks for the "cache" folder under the NEEShubloader. If it exists, it
    simply returns it's location on the system. If it doesn't exist it also creates the
    directory.'''
    cwd             = os.getcwd()
    path_index      = cwd.find('NEEShubloader')
    cache_dir       = '%sNEEShubloader/bin/cache' % (cwd[:path_index],)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

#def findCacheFile(expnum, data_type):
    
def trial_num_from_evid(expnum, evid):
    '''This is used to double check what trial number is associated with evid based on cached data.'''
    evid            = long(evid)
    evid_cache      = load_evid_dictionary(expnum)
    for key in evid_cache.keys():
        check_evid      = long(evid_cache[key])
        if evid == check_evid:
            start_index     = len('Trial-')
            trial_number    = int(key[start_index:])
            return trial_number
        

