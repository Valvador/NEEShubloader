import obspy.core

def to_epoch(UTCtime):
    '''Takes UTCtime object and makes it epoch.
    Args:
        UTCtime: String in '%Y-%m-%dT%H:%M:%S' format.
    '''
    timeformat          = '%Y-%m-%dT%H:%M:%S'
    timestr             = str(UTCtime)
    end_index           = timestr.find('.')
    cvrt_time           = timestr[:end_index]
    remainder           = timestr[end_index+1:]
    


def Trace_Msd(object):
    '''Returns a obspy.core.Stream object that contains data
    of the miniseed file.
    Args:
        filepath: Full filepath(with filename) to miniseed file.
    '''
    def __init__(self, filepath):
        self.stream    = obspy.core.read('%s' % (filepath,))
        self.trace     = self.stream[0]
        self.data      = self.trace.data
        self.stats     = self.trace.stats
        
    def to_ascii(self, outpath, calib, units):
        '''Creates a .txt file with the waveform information.
        Args:
            outpath: Filepath for output.
            calib: calibration value to take from counts to 
                physical units.
            units: Physical units used in data.
        '''
        ascii_file          = open(outpath, 'w')
        title_header        = "%s.%s%s" % (self.stats['station'],
                                           self.stats['channel'],
                                           self.stats['location'])
        delimiter           ='\t'
        header_info         ='Time%s%s%sunits\n' % (delimiter, title_header, delimiter)
        ascii_file.write(header_info)
        timeformat          = '%Y-%m-%dT%H:%M:%S'
        timestr             = str(self.stats['starttime'])
        end_index           = timestr.find('.')
        
        
        
    
        
    
        


    