#######################################################################
# Some variables needed by funcions in eds_funcs.py
# ay be altered i
#######################################################################
from os.path import expanduser

################## Eumetsat locations, don't change ##################
# API base endpoint
apis_endpoint= "https://api.eumetsat.int/"

# Searching endpoint
service_search = apis_endpoint + "data/search-products/os"

# Downloading endpoint
service_download = apis_endpoint + "data/download/"

# Navigation endpoint
service_navigator = apis_endpoint + "product-navigator/csw/record/_search"

######################################################################

################## User vars ##################
# verbose level:
#  0=quiet
#  1=errors only
#  2=warnings
#  3=messages
verbose_level=0

#if dry=True: no download, just show what would happen
dry=False

# File containing consumer_key (line 1) and consumer_secret (line 2)
keys_file='eds.key'
prod_file='eds.prd'

# Path to download location.
path_download=r"C:\Users\Baptiste\Documents\ENSG\stage\test\zipped"

# Path to location where unzipped file will be
# This location needs to be set as source location with (e.g.) xrit2pic. 
path_unzipped=r"C:\Users\Baptiste\Documents\ENSG\stage\test\unzipped"


