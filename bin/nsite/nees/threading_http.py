# Designed to offset delays from multiple uses of an HTTP call by calling threads.
import time
import threading
import nees_logging
import interface.http as ih
from config import *



#
# I. Define Threading Limit
#
pool                    = threading.BoundedSemaphore(value=semaphore_limit)

#
# II. Threading Class
#

class requestThread(threading.Thread):
    '''This is a wrapper for the http request function that allows threading.'''
    def __init__(self, request_type, request, content, headers, filename):
        threading.Thread.__init__(self)
        self.request        = request
        self.request_type   = request_type
        self.content        = content
        self.headers        = headers
        self.filename       = filename
        
    def run(self):
        '''This wraps the http request function in a threading operation.'''
        pool.acquire()
        thread_conn           = ih.http(httphost) 

        # Enables loop that attempts to post file information and breaks if successful.
#        while True:
        request_dict          = thread_conn.request(self.request_type, 
                                                    self.request, 
                                                    self.content, 
                                                    self.headers)
        location              = request_dict['location']
        data                  = request_dict['data']
        status                = request_dict['status']
        message               = "%s posted to %s. Status: %s. Reply: %s" % (self.filename,
                                                                            location, 
                                                                            status, 
                                                                            data)
        nees_logging.append_log(neeshub_log_filename, message)


            # If post fails, wait a second before retrying.
#            if status == '400':
#                time.sleep(3)  
            
            # Once Post is Successful, end the loop.
#            elif status == '200':
#                break 

        pool.release()
        
        