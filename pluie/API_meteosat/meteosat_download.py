import os
from eds_get_nearest import search_nearest, download_dataset
import sys

sys.path.insert(0, r'Images')
from File import File

sys.path.insert(0, r'tools')
from tools import make_directory

def download_SEVIRI_image(d,src_dir,keys_filename):
    try:
        zipped_dir,unzipped_dir = make_directory(src_dir+r"/zipped"),make_directory(src_dir+r"/unzipped")
        prod, Meteosat_date = search_nearest(d)
        filename = fr"{unzipped_dir}/{prod}.nat"
        if os.path.exists(filename):
            print(f"le fichier {filename} a déjà été téléchargé")
        else:
            download_dataset([prod],zipped_dir,unzipped_dir,keys_filename)
        start_date,end_date = File(filename).getAcqDates()
        return filename, start_date, end_date
    except:
        print(f"le fichier pour la date {d} n'as pas été téléchargé")
        return False