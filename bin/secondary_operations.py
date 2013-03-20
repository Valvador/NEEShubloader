#VAL GORBUNOV, NEES@UCSB
#HOLDS SECONDARY OPERATIONS FOR UPLOAD LESS-THAN-NORMAL
#EVENTS TO NEESHUB
import shutil
import nsite.nees.nees_logging as nees_logging
import nsite.http as shttp
import nsite.nees.ftp as ftp
import utils
from config import *
from nsite.nees.config import *

def delete_trials(exp_num, trial_str):
    '''Deletes trials for a specific experiment.'''
    trial_list = utils.parse_trial_request(trial_str)
    nees_logging.log_current_time(neeshub_log_filename)
    for trial in trial_list:
        try:
            shttp.delete_trial(exp_num, trial)
            hub_struct      = '/Experiment-%s/Trial-%s' % (exp_num, trial)
            trial_path = Destination + hub_struct
            shutil.rmtree(trial_path, ignore_errors=True)
            nees_logging.append_log(neeshub_log_filename, 'Trial-%s deleted.' % (trial,))
        except:
            print('No Trial-%s to delete' % (trial,))
            pass
            