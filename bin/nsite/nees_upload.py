from nees.config import *
import nees.nees_upload as upl

def upload_datafile(experiment_number, 
                    trial_number, 
                    repetition_number,
                    folder_inside_rep, 
                    source_folder, 
                    filename,
                    selector = http_file_path):
    '''Macro command that handles the entirety of the pure upload process.
    It creates the HTTP posting instance, but also uploads the actual file
    to the correct FTP location.
    Args:
        experiment_number: NEEShub Experiment Number (NOT SAME AS ID)
        trial_number: NEEShub Trial Number within the Experiment. (NOT SAME AS ID)
        repetition_number: NEEShub Repetition number within Trial. (NOT SAME AS ID)
        source_folder: Folder location of file to upload.
        filename: File's name.
        (selector): HTTP location for multipart post.'''
    upl.upload_datafile(nees_path_id, 
                        experiment_number, 
                        trial_number, 
                        repetition_number, 
                        folder_inside_rep, 
                        source_folder, 
                        filename, 
                        selector)
    
def upload_reportfile(experiment_number,
                      trial_number,
                      source_folder,
                      filename):
    '''Simplifies the report-file upload process by bypassing it's need for a specific variable.
    Args:
        experiment_number: NEEShub Experiment Number (NOT SAME AS ID)
        trial_number: NEEShub Trial Number within the Experiment. (NOT SAME AS ID)
        source_folder: Folder location of file to upload.
        filename: File's name.    
    '''
    upl.upload_reportfile(nees_path_id, 
                          experiment_number, 
                          trial_number, 
                          source_folder, 
                          filename, 
                          selector=http_file_path)