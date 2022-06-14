#!/usr/bin/python3
from os.path import expanduser
import datetime
import eds_defs
import eds_funcs

#messages: 0=quiet, 1=errors only, 2: warnings, >2: messages
eds_defs.verbose_level=2

# Key file
eds_defs.keys_file='eds.key'

#Which product to use
selected_id="EO:EUM:DAT:MSG:HRSEVIRI"

def get_nearest(date,path_dowload,path_unzipped):
    #locations
    eds_defs.path_download=path_dowload
    eds_defs.path_unzipped=path_unzipped

    time_delta = datetime.timedelta(days=1)
    start_date,end_date = date - time_delta, date + time_delta
    product_list=eds_funcs.create_list(selected_id,start_date,end_date,0)
    print(product_list)
    #eds_funcs.download_dataset(selected_id,product_list)

