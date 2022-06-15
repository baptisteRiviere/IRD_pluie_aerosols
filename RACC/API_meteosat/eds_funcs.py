#######################################################################
# Functions needed for downloading native satellite data from eumetsat
# Uses eds_defs.py
# See examples how to use.
# Some 
#######################################################################

import eds_defs
from eds_defs import verbose_level
from eds_defs import path_download
from eds_defs import path_unzipped
from eds_defs import service_search
from eds_defs import keys_file
from eds_defs import dry
from eds_defs import service_download

import os
import requests
import base64
import zipfile

# Messages, print ln if n above verbose level
# 0=quiet, 1=errors only, >1: warnings
def message(ln,n):
  if (n <= eds_defs.verbose_level):
    print(ln)


#############################################################
# Get product, specified in file 'prodfile'.
# One product each line, nr=1: use product at line 1, etc.
def get_product(prodfile,nr):
  line=""
  if os.path.isfile(prodfile):
    fp=open(prodfile,'r')
    for i in range(0,nr):
      line=fp.readline().rstrip(' \n')
    fp.close()
    return line
  else:
    message("Error: file " + prodfile + "not found.\n",1); 
    return "?"
# end def get_product

#############################################################
#List products
def list_datasets(product_list):
  message("List for download...",0)
  for product_id in reversed(product_list):
    message("in list: pd=" + product_id,3)
#end def list_datasets

#############################################################
# Get datasets for selected collection and time period
def get_datasets(selected_collection_id,start_date,end_date):
  url = eds_defs.service_search
  dataset_parameters = {'format': 'json', 'pi': selected_collection_id}
  dataset_parameters['dtstart'] = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
  dataset_parameters['dtend'] = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
  response = requests.get(url, dataset_parameters)
  found_data_sets = response.json()
  return found_data_sets
#end def get_datasets

#############################################################
# Create list for downloads. 
def create_list(selected_collection_id,start_date,end_date,nr_download):
  found_data_sets = get_datasets(selected_collection_id,start_date,end_date)
  product_list=[]
  if found_data_sets:
    n=0
    for selected_data_set in found_data_sets['features']:
      product_id = selected_data_set['properties']['identifier']
      if ((nr_download==0) | (n<nr_download)):
        product_list=product_list + [product_id]
      n=n+1
    return product_list
#end def create_list

#############################################################
def remove_not_in_dataset(product_list):
  for fn in os.listdir(eds_defs.path_download):
    if (fn.endswith(".zip")):
      found=False
      for product_id in reversed(product_list):
        fnd=product_id + ".zip"
        if (fn == fnd):
          found=True
          break
      if (not found):
        pfn=eds_defs.path_download + "/" + fn
        if (eds_defs.dry):
          message("dry flag set; Would remove " + pfn,2)
        else:
          message("Remove " + pfn,2)
          os.remove(pfn)
#end def remove_not_in_dataset

#########################Download##############################
# Download 'product_id' into file 'fn', using 'access_token'
# pfn should contain full path
# 
def download(access_token,collection_id,product_id,pfn):
  use_wget=True
  message("Get "+ product_id + " to " + pfn,4)
  download_url = service_download + 'collections/' + collection_id + '/products/' + product_id

  get_url = download_url + '?access_token=' + access_token
  if (use_wget):
    # Use wget
    if (eds_defs.verbose_level>=4):
      stil=""
    else:
      stil="-q"
    cmd="wget " + stil + " --timeout=100 " + get_url + " -O " + pfn
    message(cmd,4)
    os.system(cmd)
  else:
    # Use Python download; needs lots of memory...
    response = requests.get(download_url,stream = True, headers={'Authorization':'Bearer ' + access_token})
    requests.get(get_url, allow_redirects=True)
    with open(pfn, 'wb') as f:
      f.write(response.content)

  return
#end def download


#############################################################
# Download one zipped 'product' to location 'path_download'
#   unzip into location 'path_unzipped'
#   return: 
#     0 if downloaded
#     1 if zip-file already present, don't download
#     2 if downloaded file is not a zip file
def download_zipped_product(collection_id,product_id,access_token):
  zfn=product_id+'.zip'
  print(path_download)
  pzfn=path_download+"/"+zfn
  
  if os.path.isfile(pzfn):
    message("Already downloaded: " + pzfn,3)
    return 1
  else:
    if (not eds_defs.dry):
      message("Going to Download " + product_id,4)
      download(access_token,collection_id,product_id,pzfn)
      message("Downloaded " + zfn,3)

      if zipfile.is_zipfile(pzfn):
        message("Unzip " + zfn,3);
        with zipfile.ZipFile(pzfn,'r') as zipObj:
          zipObj.extractall(path=eds_defs.path_unzipped)
        return 0
      else:
        message("WARNING: " + zfn + " not a zipfile; skipped.",2)
        return 2
    else:
      message("dry flag set; Would Download " + product_id,3)
  return 0
#end def download_zipped_product


###############################API token##############################
# Get token from https://api.eumetsat.int/token
# Keys in eds.key:
#   line 1: consumer_key
#   line 2: consumer_secret
def get_token():
#  global consumer_key
#  global consumer_secret
  print(eds_defs.keys_file)
  if os.path.isfile(eds_defs.keys_file):
    fp=open(eds_defs.keys_file,'r')
    consumer_key=fp.readline().rstrip(' \n')
    consumer_secret=fp.readline().rstrip(' \n')
    fp.close()
  else:
    message("ERROR: No key file " + eds_defs.keys_file + " found.",1)
    exit()
    
  client_id = consumer_key       
  client_secret = consumer_secret
  to_encode = client_id + ':' + client_secret
  base64_encoded_id_secret = base64.b64encode(to_encode.encode()).decode()

  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic {}'.format(base64_encoded_id_secret)
  }

  params = {'grant_type': 'client_credentials'}
  r = requests.post('https://api.eumetsat.int/token', headers=headers, params=params)
  print(r.json())
  access_token = r.json()['access_token']
  return access_token
# end def get_token

#############################################################
# Download  set of files, from start_date to end_date (use datetime())
#   and Unzip
def download_dataset(selected_id,product_list):
  collection_id=selected_id.replace(":","%3A")
  if product_list:
    access_token = get_token()

    for product_id in reversed(product_list):
      download_zipped_product(collection_id,product_id,access_token)
#end def download_dataset

