#Basic FTP Module to designed to abstract a httplib layer to a somewhat low level.
#Created by Val Gorbunov for the use of NEES@UCSB
import datetime
import httplib


#TODO: NEED TO ADD DELETE FUNCTIONS
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# I. INITIALIZATION
# All variables should be defined within __init__ function.
# Username and Password are their own definition due to their use in FTP as well.
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class http(object):
    '''This Class creates an establishes a connection with the neeshub server. This does everything, from reading the neeshub
    webservices API's returns to creating new Trials. Current integration requires Pen Tool for uploading actual data and serves
    more as an intermediary between our system and the neeshub servers.'''
    def __init__(self, host):
        
        self.host       = host
        self.conn       = None
        self.inlist     = []    
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
        
    def request(self, request_type, request_parameter, content='', headers=''):
        """Sends request to http server.
        
        Args:
            request_type: Type of HTTP request. IE: "GET", "POST"...
            request_parameter: URL extension for where to send request.
            (content): Content sent to locations defined by
                request_parameter. Usually used in "POST" requests.
            (headers): Header content sent to request_parameter.
        Returns:
            dictionary with keys: 'status', 'data', 'location'
                'status': HTTP request status.
                'data': HTTP response.
                'location': HTTP response header for location.
        """
        self.connect()
        if (content == '' and headers == ''):
            self.conn.request(request_type, request_parameter)
        else:
            self.conn.request(request_type, request_parameter, content, headers)
        res         = self.conn.getresponse()
        status      = res.status    
        data        = res.read()
        location    = ''
        try:
            location = res.getheader('location')
        except:
            pass
        return {'status' : status,'data' : data, 'location' : location}          
