import os
from datetime import datetime, timedelta, date
import sys
import numpy as np
import json

from nsidc_download import cmr_download,cmr_search

sys.path.insert(0, r'Images')
from File import File


def download_url_list(download_dir,url_list,d,projection,zero_rate_min=0.2,format="%Y-%m-%dT%H:%M:%S.%f%z",attribut="TB"):

    tg_date = datetime.strptime(d,format)
    for url in url_list:
        if url[-2:] == "nc":
            filename = download_dir+ "/" + url.split('/')[-1]
            if os.path.exists(filename):
                print(f"the file {filename} has already been downloaded")
            else:
                print(f"the file {filename} is being downloaded")
                cmr_download([url,url+".xml"], download_dir, quiet=True)
            file = File(filename)
            img = file.project(projection,attribut)
            try : # on compte les occurences de 0 pour déterminer si le fichier est corrompu
                unique, counts = np.unique(img.array, return_counts=True)
                zero_rate = dict(zip(unique, counts))[0]/(img.array.shape[0]*img.array.shape[1])
            except KeyError: # aucune occurence de 0
                zero_rate = 0
            start_date, end_date = file.getAcqDates()
            print(f"image analysée : zero_rate={zero_rate}, start_date: {start_date}, end_date: {end_date}")
            if (zero_rate < zero_rate_min):
                print(f"image trouvée à la date {d}")
                img.show()
                return filename, start_date, end_date
    
    return False

def download_Meteosat_images(d,download_dir,projection,research_parameters,format="%Y-%m-%dT%H:%M:%S.%f%z",zero_rate_min=0.2,recurs_iter=0):
    
    print(f"_____\nrecherche pour la date {d}")

    grid = research_parameters["grid"][recurs_iter]
    capteur = research_parameters["capteur"][recurs_iter]
    freq = research_parameters["freq"][recurs_iter]
    passage = research_parameters["passage"][recurs_iter]
    algo = research_parameters["algo"][recurs_iter]

    tg_date = datetime.strptime(d,format)
    tg_year = tg_date.year
    delta = timedelta(hours=12)
    min_date,max_date = tg_date-delta,tg_date+delta
    
    url_list = cmr_search(  short_name='NSIDC-0630', 
                            version='1', 
                            time_start=datetime.strftime(min_date,"%Y-%m-%dT%H:%M:%S")+"Z",
                            time_end=datetime.strftime(max_date,"%Y-%m-%dT%H:%M:%S")+"Z",
                            bounding_box='-61.27,-2.38,-47.66,10.86',
                            filename_filter=f'NSIDC-0630-EASE2_{grid}-{capteur}-{tg_year}*-{freq}-{passage}-{algo}*', 
                            quiet=True)
    
    retour = download_url_list(download_dir,url_list,d,projection,zero_rate_min)
    if retour :
        return retour
    elif recurs_iter < len(research_parameters["grid"]) -1:
        print("on plonge en profondeur capitaine")
        recurs_iter += 1
        return download_Meteosat_images(d,download_dir,projection,research_parameters,format,zero_rate_min,recurs_iter)
    return False
