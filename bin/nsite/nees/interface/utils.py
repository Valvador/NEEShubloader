#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# III. MySQL module auxiliary functions.
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------           
    
def generate_site_description_string(list_of_sites = None):
    '''This function exists specifically to generate a mysql-friendly statement that allows to filter the lookup tables based on site.
    Basically if you pass a list ['1','100','101'] into it, the returned string would read " and (site = 1 or site = 100 or site = 101)"'''
    # Initiate the included filtering conditions by starting with an "and".
    if list_of_sites is not None:
        site_select = ' and ('                                                                            
        
        # Create a sequence of "or" conditions for the possible match of "site" variable.
        for site in list_of_sites:
            site_select +=  "site = '%s' or " % (site,)
        select_string = site_select[0:len(site_select)-4] +')'                                   
    
    # If site definition is irrelevant, pass an empty string.
    else:
        select_string = ''
    
    # Returns an additional condition for mySQL filtering.    
    return select_string

def generate_station_description_string(list_of_sites = None):
    '''This function exists specifically to generate a mysql-friendly statement that allows to filter the lookup tables based on site.
    Basically if you pass a list ['1','100','101'] into it, the returned string would read " and (site = 1 or site = 100 or site = 101)"'''
    # If there is station name condition, initiate the included filtering conditions by starting with an "and".
    if list_of_sites is not None:
        site_select = ' and ('                                                                            
        
        # Create a sequence of "or" conditions for the possible match of "sta" variable.            
        for site in list_of_sites:
            site_select +=  "sta = '%s' or " % (site,)
        select_string = site_select[0:len(site_select)-4] +')'                                   

    # If there is no station name condition return empty condition.
    else:
        select_string = ''
    
    # Returns additional condition for mySQL filtering.
    return select_string
        
        