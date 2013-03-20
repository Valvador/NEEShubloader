#This module scans the existing format of the NEES webpage, and checks last uploaded trial.
import datetime
import httplib
import getpass
import utils
import nees_logging
import neesftp_interface as bni
import multipart_http
from config import *


    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# I. INITIALIZATION
# All variables should be defined within __init__ function.
# Username and Password are their own definition due to their use in FTP as well.
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
hub_username   = raw_input('NEEShub username:')                      
hub_password   = getpass.getpass('NEEShub password:') 


class NEEShttp(object):
    '''This Class creates an establishes a connection with the neeshub server. This does everything, from reading the neeshub
    webservices API's returns to creating new Trials. Current integration requires Pen Tool for uploading actual data and serves
    more as an intermediary between our system and the neeshub servers.'''
    def __init__(self, host = httphost, username = hub_username, password = hub_password):
        
        self.host       = host
        self.conn       = None
        self.inlist     = []
        self.username   = username                      
        self.password   = password      
        self.connect()

    def connect(self):
        '''Basic function that establishes a connection using httplib's HTTPSConnection with the host.
        This has to be added at the end of every function, otherwise no following requests will be able
        to go through as HTTPSConnection can only handle one request.'''
        if self.conn is not None:
            self.conn.close()
            del self.conn
            self.conn = None
        self.conn = httplib.HTTPSConnection(self.host)
        
    def make_request(self, request_type, request_parameter):
        '''Primary function of the NEEShub Interface module.
        This function should be used for all basic requests made to NEEShub. 
        request_type should be a typical HTTP style request. For example: "GET"
        request_parameter should be the location where inside the NEEShub this request should be made.
        For example if you want to make a "GET" request to "neesws.neeshub.org:9443/REST/Project/353" make
        request_type = "GET" and request_parameter = "/REST/Project/353".
        This will return a dictionary with values for "status", "data", and "location" with HTTP Status, XML Data, and
        location header respectively.
        If you only want to see the XML Data of the previously mentioned command use the following syntax:
        >>>data = self.make_request("GET","/REST/Project/353")['data']'''
        self.conn.request(request_type,"%s?GAsession=%s/%s" % (request_parameter, self.username, self.password))
        res = self.conn.getresponse()
        status = res.status    
        data = res.read()
        location = ''
        try:
            location = res.getheader('location')
        except:
            pass
        self.connect()
        return {'status' : status,'data' : data, 'location' : location}          

#----------------------------------------------------------------------------------------------------------------------------------------------------------
# II. RETRIEVAL FUNCTIONS
#----------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_experiment_id_dictionary(self):
        '''Function which searches through neeshub project 353 for a structure of experiments. Prints
        out the ID of the experiments in no particular order. Safe to assume the Experiment ID is the
        same order as the Experiment #'''
        data = self.make_request("GET","/REST/Project/353")['data']
        index = 0
        experimentstring = "/REST/Project/353/Experiment/"
        self.inlist = []
        self.experiment_dict = {}
        while index < len(data):                     #CHECK FOR ALL OCCURANCES OF 'EXPERIMENT-' TO LOCATE THE WEBSERVICE DATASTRUCTURE.
            index=data.find(experimentstring,index)
            if index == -1:
                break
            index += len(experimentstring)           #MOVE INDEX TO WHERE EXPERIMENT NUMBER IS
            self.inlist.append(index)
            endindex        = index+data[index:].find('" id=')
            name_start      = '<name>'
            name_end        = '</name>'
            name_index      = endindex + data[endindex:].find(name_start) + len(name_start)
            name_endindex   = name_index + data[name_index:].find(name_end)
            dictkey         = data[name_index:name_endindex]  
            dictval         = data[index:endindex]
            self.experiment_dict[dictkey] = dictval
        print self.inlist    
        return self.experiment_dict
        

    def get_trial_id_dictionary(self, experiment_number):
        '''Similar to get_experiment_id_dictionary(). This takes an acquired experiment ID as it's input and searches
        for the analogous structure of trials within the experiment. This returns a dictionary of Trials
        from within the experiment.'''
        experimentId    = experiment_id[experiment_number]        
        requestDict     = self.make_request("GET","%sExperiment/%s" % (neeshub_project_path, experimentId)) 
        data            = requestDict['data']
        index           = 0
        experimentstring = "/REST/Project/353/Experiment/%s/Trial/"  % (experimentId)      
        self.experimentdict = {}
        while index < len(data):                     #CHECK FOR ALL OCCURANCES OF 'TRIAL-' TO LOCATE THE WEBSERVICE DATASTRUCTURE.
            index       = data.find(experimentstring,index)
            index_tnum  = data.find("Trial-",index)
            if index == -1:
                break
            index += len(experimentstring)           
            trialID     = data[index:data.find('" id',index)]
            trialNum    = data[index_tnum:data.find('</name>',index)]
            self.experimentdict[trialNum] = trialID
        self.connect()
        return self.experimentdict          
    
    def get_trial_metadata_dictionaries_partial(self, experiment_number, experimentdict):
        '''This creates a dictionary of dictionaries that is organized as such: {Trial-#:{'evid': 12345, 'magnitude': 4.02, 'distance': 124}}.
        This makes it much easier for the information stored to be parsed through by utilizing a double index to get the specific piece of 
        of information about the specific Trial.'''
        experimentId        = experiment_id[experiment_number]
        cache_evid_dict     = {}
        cache_ml_dict       = {}
        cache_distance_dict = {}
        for trial in experimentdict:
            requestDict     = self.make_request("GET","/REST/Project/353/Experiment/%s/Trial/%s" % (experimentId, experimentdict[trial]))
            data            = requestDict['data']
            evid            = utils.parse_description('evid:', data)
            magnitude       = utils.parse_description('ml:', data)
            distance        = utils.parse_description('distance:', data)
            cache_evid_dict[trial]        = utils.convert_to_long(evid)
            cache_ml_dict[trial]          = utils.convert_to_float(magnitude)
            cache_distance_dict[trial]    = utils.convert_to_float(distance)
            nees_logging.log_cache_invalid_cache_variables(trial, cache_evid_dict[trial],cache_ml_dict[trial],cache_distance_dict[trial])
        return cache_evid_dict, cache_ml_dict, cache_distance_dict
    
    def get_trial_metadata_dictionaries(self, experiment_number):
        '''Combines get_trial_id_dictionary and get_trial_metadata_dictionaries_partial so that they only thing the user needs to input is the experiment_number
        in order to lessen the micromanaging required from the user.'''
        experimentdict                  = self.get_trial_id_dictionary(experiment_number)
        evid_dict, ml_dict, dist_dict   = self.get_trial_metadata_dictionaries_partial(experiment_number, experimentdict)
        return evid_dict, ml_dict, dist_dict


#------------------------------------------------------------------------------------------------------------------------------------------------
# III. Posting functions. Below here are included functions that post (DO NOT UPLOAD DATA) to the NEEShub.
#------------------------------------------------------------------------------------------------------------------------------------------------

            

    def post_trial(self,experimentId,trialtitle,description):                               #TODO: VARIABLE CONTENT, instead of template.        
        '''This uses webservices API to create trials within an experiment.'''
        
        content         = """                                                   
                        <Trial curationStatus="Uncurated" >          
                            <title>"""+trialtitle+"""</title>
                            <description>"""+description+"""</description>
                            <status>private</status>
                        </Trial>"""
        
        headers         = {'Host': self.host,
                           'Accept': 'application/xml',
                           'Content-Type': 'application/xml',
                           'Content-Length': str(len( content ))  }  
        
        request_path    = "%sExperiment/%s/Trial?GAsession=%s/%s" % (neeshub_project_path, experimentId, self.username, self.password)
        
        self.conn.request("POST",request_path, content, headers) 
        res             = self.conn.getresponse()
        triallocation   = res.getheader('location')  
        id_index        = triallocation.find('/Trial/')
        id_offset       = len('/Trial/')
        self.connect()
        return triallocation[id_index+id_offset:]
    

    def post_rep(self,experimentId,TrialId):       
        '''This is a continuation of the post_trial function. Since Trials usually have a Repetition 
        folder inside of them, populate our Trials with a Repetition structure. If input ExperimentID 
        and TrialID this will create a Rep-1 Folder. '''
        
        content         = """
                            <Repetition curationStatus="Uncurated" >
                                <startDate>2005-08-16T00:00:00-07:00</startDate>
                                <endDate>2005-08-16T00:00:00-07:00</endDate>
                            </Repetition>"""
        
        headers         = {'Host': self.host,
                           'Accept': 'application/xml',
                           'Content-Type': 'application/xml',
                           'Content-Length': str(len( content ))  }  
        
        request_path    = "%sExperiment/%s/Trial/%s/Repetition?GAsession=%s/%s" % (neeshub_project_path, experimentId, TrialId, self.username, self.password)

        self.conn.request("POST",request_path, content, headers) 
        res             = self.conn.getresponse()
        replocation     = res.getheader('location')  
        id_index        = replocation.find('/Repetition/')
        id_offset       = len('/Repetition/')
        self.connect()
        return replocation[id_index+id_offset:] 
   
    def post_full_trial(self,experimentId,trialtitle,description, trial_number):
        '''Creates a Trial with a Repetition folder inside an experiment. Elaborate function furtherS'''
        trialid         = self.post_trial(experimentId,trialtitle,description)
        repid           = self.post_rep(experimentId,trialid)
        nees_logging.log_trial_creation(trial_number, experimentId, trialid, repid)
        self.connect()
        print "Created: "+repid+" inside Trial: "+trialid
         

    
    def multipart_post(self, filename, expnum, trialnum, ext, selector = http_file_path, verbose = False):
        '''This is technically an upload post. It assumes that there has already been an FTP file uploaded
        to the NEEShub and is simply waiting assignment. This post will be the assignment.'''
        full_filename       = filename + ext
        xml_sheet           = multipart_http.generate_file_xml(full_filename, expnum, trialnum, ext)
        content_type, body  = multipart_http.encode_multipart_formdata(xml_sheet, full_filename, self.username, self.password)


        headers         = { 
                           'Host'          : self.host,
                           'Content-Type'  : content_type,
                           'Content-Length': str(len(body))
                           }


        request_path = '%s?GAsession=%s/%s' % (selector, self.username, self.password)
        self.conn.request('POST',request_path, body, headers)
        res = self.conn.getresponse()
        return res.status, res.reason, res.read(), res.getheader('location')
 

    def multipart_post_generic(self, filename, expnum, trialnum, selector = http_file_path, verbose = False):
        '''This is technically an upload post. It assumes that there has already been an FTP file uploaded
        to the NEEShub and is simply waiting assignment. This post will be the assignment.'''
        full_filename       = filename
        xml_sheet           = multipart_http.generate_report_xml(full_filename, expnum, trialnum)
        content_type, body  = multipart_http.encode_multipart_formdata(xml_sheet, full_filename, self.username, self.password)


        headers         = { 
                           'Host'          : self.host,
                           'Content-Type'  : content_type,
                           'Content-Length': str(len(body))
                           }


        request_path = '%s?GAsession=%s/%s' % (selector, self.username, self.password)
        self.conn.request('POST',request_path, body, headers)
        res = self.conn.getresponse()
        return res.status, res.reason, res.read(), res.getheader('location')
 

#--------------------------------------------------------------------
# DEBUG/OBSOLETE
#--------------------------------------------------------------------

    def multipart_multifile_post(self, filenames, expnum, trialnums, selector = http_file_path, verbose = False):
        '''This attempts to make a NEEShub post that involves MULTIPLE files all at once.'''
        paths               = multipart_http.generate_paths(expnum, trialnums)        
        xml_sheets          = multipart_http.generate_upload_xmls(filenames, paths)
        content_type, body  = multipart_http.encode_multipart_forms(xml_sheets, filenames, self.username, self.password)
 
        headers         = { 
                           'Host'          : self.host,
                           'Content-Type'  : content_type,
                           'Content-Length': str(len(body))
                           }


        request_path = '%s?GAsession=%s/%s' % (selector, self.username, self.password)
        self.conn.request('POST',request_path, body, headers)
        res = self.conn.getresponse()
        return res.status, res.reason, res.read(), res.getheader('location')

        
#--------------------------------------------------------------------------------------
# Launch NEEShub Web-Services Instance - 
#-------------------------------------------------------------------------------------- 
conn = NEEShttp(username = hub_username, password = hub_password)
#--------------------------------------------------------------------------------------
# Launch NEEShub ftp Instance - 
#--------------------------------------------------------------------------------------
ftpconn = bni.NEESftp(username = hub_username, password = hub_password) 



