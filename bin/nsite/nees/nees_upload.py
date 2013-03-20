from config import *
import ftp
import http
import utils

def upload_datafile(nees_path_id,
                    experiment_number, 
                    trial_number, 
                    repetition_number,
                    folder_inside_rep, 
                    source_folder, 
                    filename,
                    selector = http_file_path):
    '''Macro command that handles the entirety of the pure upload process.
    It creates the HTTP posting instance, but also uploads the actual file
    to the correct FTP location.
    '''
    source_path         = "%s/%s/%s" % (source_folder, folder_inside_rep, filename)
    ftp.upload_to_project(filename, source_path)
    http.multipart_post(filename, 
                        nees_path_id, 
                        experiment_number, 
                        trial_number,
                        repetition_number, 
                        folder_inside_rep, 
                        selector,
                        threading = threading_on) 
    
def upload_reportfile(nees_path_id,
                      experiment_number,
                      trial_number,
                      source_folder,
                      filename,
                      selector = http_file_path):
    '''Macro command that handles the report upload process for any NEEShub
    project defined within the variables.'''
    source_path     = source_folder + filename
    ftp.upload_to_project(filename, source_path)
    http.multipart_post_generic(filename, nees_path_id, experiment_number, trial_number, selector)
    
    