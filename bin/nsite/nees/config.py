#EDIT THIS FILE TO DEFINE VARIABLES, ADD NEW EXPERIMENT ID'S
'''If you are updating this file with a new experiment, please make sure you create
a new entry under experiment_id and experiment_path under the same corresponding
key.'''

#
# I. User Specific Variables
#

# DEFINES NEESHUB'S FTP-FOLDER LOCATION OF USER
# SPECIFIC PROJECT. FOR PROPER USE WITH YOUR
# SYSTEM THIS VARIABLE MUST BE DEFINED IN THE FORMAT
# "NEES-YEAR-proID.groups". THIS IS ARBITRARILY
# ASSIGNED TO ALL NEESHUB PROJECTS
nees_path_id             = "NEES-2007-0353.groups"
# Log filename. Name whatever you want.
neeshub_log_filename    = "NEEShub.log"
# SITE-SPECIFIC NEES PROJECT ID
sitenees_proj           = '353'


#
# II. NEEShub Variables
#

# NEEShub authentication string to add to the end of URL
neeshub_auth_format     = "%s?GAsession=%s/%s"
# First part of NEEShub project location within Webservices
neeshub_project_path    = "/REST/Project/"
# NEEShub Webservices hostname and port.
httphost                = "neesws.neeshub.org:9443"
# NEEShub FTP hostname.
ftphost                 = "neesws.neeshub.org"
# NEEShub project folder layout inside ftp. Generally "/.upload/NEES-YEAR-proID.groups/"
nees_prj_fld            = '/.upload/%s/' % (nees_path_id,)
# Location where HTTP file posts should be made to.
http_file_path          = '/REST/DataFile'

#
# III. Threading Variables
#

threading_on            = False
semaphore_limit         = 10

