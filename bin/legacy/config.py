#EDIT THIS FILE TO DEFINE VARIABLES, ADD NEW EXPERIMENT ID'S
'''If you are updating this file with a new experiment, please make sure you create
a new entry under experiment_id and experiment_path under the same corresponding
key.'''


Default_Folder = "/nami/dbproc/pub/"                 #MAKE SURE THE REPLACE THIS IN FINAL RELEASE.



#
# I. NEEShub Variables
#

Destination             = "/Users/Shared/PEN/"
neeshub_project_path    = "/REST/Project/353/"
neeshub_log_filename    = "NEEShub.log"
httphost                = "neesws.neeshub.org:9443"
ftphost                 = "neesws.neeshub.org"
nees_prj_id             = "NEES-2007-0353.groups"
nees_prj_fld            = '/.upload/NEES-2007-0353.groups/'
http_file_path          = '/REST/DataFile'

#__________________EXPERIMENT ID____________________________
experiment_id = {'1':"592",
                 '2':"610",
                 '3':"4101",
                 '4':"4102",
                 '5':"4103"}


#__________________EXPERIMENT FILE PATH_____________________
experiment_path = {'1':Destination+"Experiment-1/",
                   '2':Destination+"Experiment-2/",
                   '3':Destination+"Experiment-3/",
                   '4':Destination+"Experiment-4/",
                   '5':Destination+"Experiment-5/"}

#__________________EXPERIMENT DESCRIPTION___________________
experiment_description =     {'1': "Please Add Description",
                              '2': "Please Add Description",
                              '3': "Please Add Description",
                              '4': "Nightly variable frequency sweep of the SFSI structure located at Garner Valley",
                              '5': "Nightly Cross-Hole tests using geophones with a source at 5 meters. "}

#__________________EXPERIMENT TITLE TIME_____________________
experiment_title_time =      {'1': "Please Add Description",
                              '2': "Please Add Description",
                              '3': "Please Add Description",
                              '4': "00:00:00",
                              '5': ""}

#__________________EXPERIMENT TITLE STRUCTURE________________
experiment_title_struct =  {'1': "UNDEFINED",                   #TODO
                            '2': "UNDEFINED",                   #TODO
                            '3': "UNDEFINED",                   #TODO
                            '4': "%Y%j",                        #YearJulian
                            '5': "%Y%j"}                        #YearJulian

#__________________EXPERIMENT METADATA METHOD______________
experiment_meta_type = {'1':'mysql',
                        '2':'mysql',
                        '3':'mysql',
                        '4':'hammers and sfsi',
                        '5':'hammers and sfsi'}

#__________________EXTENSION FOLDER________________________
cfg_hub_ext_fold    = {'.msd':'Corrected_Data',
                       '.sac':'Converted_Data',
                       '.txt':'Derived_Data'}

#
# II. MySQL Variables
#


#__________________MYSQL SITE DEFINITIONS______________________
mySQL_sitedef = {'1': ['2'],
                 '2': ['1','100','101'],
                 '3': ['201'],
                 '4': None,
                 '5': None}

#__________________MYSQL STA DEFINITIONS_______________________
mySQL_stadef = {'1':['GVA','GVDA'],
                '2':['WLA','5210','SAAR'],
                '3':['SFSI'],
                '4':None,
                '5':None,}


#__________________EVENT TABLE VALUE KEYS______________________
cfg_evt_site                        = 'site'
cfg_evt_siteEvt                     = 'siteEvt'
cfg_evt_evid                        = 'evid'
cfg_evt_azm                         = 'azmith'
cfg_evt_dist                        = 'dist'
cfg_evt_time                        = 'time'
cfg_evt_ml                          = 'ml'
cfg_evt_lat                         = 'lat'
cfg_evt_lon                         = 'lon'
cfg_evt_depth                       = 'depth'

#__________________FILE TABLE VALUE KEYS_______________________
cfg_fl_segtype                     = 'segtype'
cfg_fl_calib                       = 'calib'
cfg_fl_dfile                       = 'dfile'
cfg_fl_net                         = 'net'
cfg_fl_sta                         = 'sta'
cfg_fl_chan                        = 'chan'


#__________________CHANNEL TABLE VALUE KEYS____________________
cfg_chan_pchan                     = 'pubChan'
cfg_chan_dpth                      = 'depth'
cfg_chan_noffset                   = 'offsetN'
cfg_chan_eoffset                   = 'offsetE'

#__________________MYSQL INTERFACE_____________________________
mySQL_host                         = 'fern.nees.ucsb.edu'
mySQL_database_name                = 'dportal'
mySQL_description_table            = 'lookup'
mySQL_file_table                   = 'trace'
mySQL_lookup_order                 = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (cfg_evt_site, cfg_evt_siteEvt, cfg_evt_evid, cfg_evt_azm, cfg_evt_dist, cfg_evt_time, cfg_evt_ml, cfg_evt_lat, cfg_evt_lon, cfg_evt_depth)
mySQL_minimum_magnitude            = "400"                             #Give Magnitude in units of Magnitude X100

#__________________MYSQL CALIB UNITS___________________________
#http://private.nees.ucsb.edu/wiki/index.php/CSS_3.0_schma_notes
#Keep up to date. Possible consider making a script that generates the below Dict.
mySQL_calibdef = {'A'    :   'nm/sec/sec',        #acceleration
                  'B'    :   '25*mw/m/m',         #UV (sunburn) index (NOAA)
                  'D'    :   'nm',                #displacement
                  'H'    :   'pascal',            #hydroacoustic
                  'I'    :   'pascal',            #infrasound
                  'J'    :   'watts',             #power (Joules/sec) (UCSD)
                  'K'    :   'kilopascal',        #generic pressure (UCSB)
                  'M'    :   'millimeters',       #Wood-Anderson drum recorder
                  'N'    :   '-',                 #dimensionless
                  'P'    :   'millibar',          #barometric pressure
                  'R'    :   'millimeters',       #rain fall (UCSD)
                  'S'    :   'nm/m',              #strain
                  'T'    :   'seconds',           #time
                  'V'    :   'nm/sec',            #velocity
                  'W'    :   'watts/m/m',         #insolation
                  'X'    :   'nm*sec',            #integrated displacement
                  'Y'    :   'power',             #waveform power
                  'a'    :   'degrees',           #azimuth
                  'b'    :   'bits/second',       #bit rate
                  'c'    :   'counts',            #dimensionless integer
                  'd'    :   'meters',            #depth or height (e.g., water)
                  'f'    :   'micromoles/s/m/m',  #photoactive radiation flux
                  'h'    :   'pH',                #hydrogen ion concentration
                  'i'    :   'amperes',           #electric current
                  'l'    :   'sec/km',            #slowness
                  'm'    :   'bitmap',            #dimensionless bitmap
                  'n'    :   'nanoradians',       #angle (tilt)
                  'o'    :   'milligrams/liter',  #dilution of oxygen (Mark VanScoy)
                  'p'    :   'percent',           #percentage
                  'r'    :   'inches',            #rainfall (UCSD)
                  's'    :   'meter/second',      #speed (e.g., wind)
                  't'    :   'degrees_Celsius',   #temperature
                  'u'    :   'microsiemens/cm',   #conductivity
                  'v'    :   'volts',             #electric potential
                  'w'    :   'radians/second'}    #rotation rate


#__________________TIME FORMAT_________________________________
default_time_format             = '%m-%d-%Y %H:%M:%S'
data_retrieval_time_format      = '%Y/%j/'
