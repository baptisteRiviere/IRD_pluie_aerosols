import os
from datetime import datetime, timedelta, date
import sys
import numpy as np
import json

from nsidc_download import cmr_download,cmr_search

sys.path.insert(0, r'Images')
from File import File


def download_url_list(download_dir,url_list,tg_date,projection,keys_filename,no_data_rate_min=0.2,format="%Y-%m-%dT%H:%M:%S.%f%z",attribut="TB",quiet=False):

    for url in url_list:
        if url[-2:] == "nc":
            filename = download_dir+ "/" + url.split('/')[-1]
            if os.path.exists(filename):
                if not quiet:
                    print(f"the file {filename} has already been downloaded")
            else:
                if not quiet:
                    print(f"the file {filename} is being downloaded")
                cmr_download([url,url+".xml"], download_dir, keys_filename, quiet=True)
            file = File(filename)
            img = file.project(projection,attribut)
            no_data_rate = np.count_nonzero(np.isnan(img.array))/(img.array.shape[0]*img.array.shape[1])
            start_date, end_date = file.getAcqDates()
            if not quiet:
                print(f"image analysée : no_data_rate={no_data_rate}, start_date: {start_date}, end_date: {end_date}")
            if no_data_rate < no_data_rate_min:
                if not quiet:
                    print(f"image trouvée à la date {tg_date}")
                    img.show()
                return filename, start_date, end_date
    
    return False

def download_SSMIS_image(tg_date,download_dir,projection,research_parameters,keys_filename,format="%Y-%m-%dT%H:%M:%S.%f%z",no_data_rate_min=0.2,recurs_iter=0,quiet=False):
    
    print(f"SSMIS : recherche pour la date {tg_date}")

    try:
        grid = research_parameters["grid"][recurs_iter]
        capteur = research_parameters["capteur"][recurs_iter]
        freq = research_parameters["freq"][recurs_iter]
        passage = research_parameters["passage"][recurs_iter]
        algo = research_parameters["algo"][recurs_iter]

        tg_year = tg_date.year
        delta = timedelta(hours=12)
        min_date,max_date = tg_date-delta,tg_date+delta
        
        url_list = cmr_search(  short_name='NSIDC-0630', 
                                version='1', 
                                time_start=datetime.strftime(min_date,"%Y-%m-%dT%H:%M:%S")+"Z",
                                time_end=datetime.strftime(max_date,"%Y-%m-%dT%H:%M:%S")+"Z",
                                bounding_box='-61.27,-2.38,-47.66,10.86',
                                filename_filter=f'NSIDC-0630-EASE2_{grid}-{capteur}-{tg_year}*-{freq}-{passage}-{algo}*', 
                                quiet=quiet)
        
        retour = download_url_list(download_dir,url_list,tg_date,projection,keys_filename,no_data_rate_min,quiet=quiet)
        if retour :
            return retour
        elif recurs_iter < len(research_parameters["grid"]) -1:
            if not quiet:
                print("SSMIS : récurisvité")
            recurs_iter += 1
            return download_SSMIS_image(tg_date,download_dir,projection,research_parameters,keys_filename,format,no_data_rate_min,recurs_iter,quiet=quiet)
    except :
        print(f"SSMIS : le fichier pour la date {tg_date} n'as pas été téléchargé")
        return False
    return False
