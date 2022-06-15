#!/usr/bin/python3
from os.path import expanduser
import datetime
import eds_defs
import eds_funcs
import numpy as np

#messages: 0=quiet, 1=errors only, 2: warnings, >2: messages
eds_defs.verbose_level=2

# Key file
eds_defs.keys_file='eds.key'

#Which product to use
selected_id="EO:EUM:DAT:MSG:HRSEVIRI"

def search_nearest(date):
    time_delta = datetime.timedelta(minutes=30)
    start_date,end_date = date - time_delta, date + time_delta
    product_list=eds_funcs.create_list(selected_id,start_date,end_date,0)
    
    delta_min, nearest_prod = np.iinfo(np.int32).max, None
    for prod in product_list: # recherche de l'acquisition pendant la période
        end_acq_Meteosat = datetime.datetime.strptime(prod.split("-")[5].split(".")[0]+"+00:00", '%Y%m%d%H%M%S%z')
        delta = (end_acq_Meteosat-date).total_seconds()
        if (delta >= 0) and (delta < delta_min):
            delta_min, nearest_prod = delta, prod
    return nearest_prod, datetime.datetime.strptime(nearest_prod.split("-")[5].split(".")[0]+"+00:00", '%Y%m%d%H%M%S%z')
   
def download_dataset(product_list,path_download,path_unzipped,keys_file):
    #locations
    eds_defs.path_download=path_download
    eds_defs.path_unzipped=path_unzipped
    eds_defs.keys_file=keys_file

    eds_funcs.download_dataset(selected_id,product_list)

