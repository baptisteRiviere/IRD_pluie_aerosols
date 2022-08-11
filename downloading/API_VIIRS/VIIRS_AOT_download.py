import os, shutil
import urllib.request as request
from contextlib import closing
from datetime import datetime
import gzip
import sys

sys.path.insert(0, r'../tools')
from tools import get_index,save_index,make_directory

sys.path.insert(0, r'../Images')
from File import File


def download_VIIRS_image(d,out_dir):
    d = datetime.strptime(d,"%Y-%m-%dT%H:%M:%S.%f%z")
    d_str = datetime.strftime(d,"%Y%m%d")

    #set url from where to download files 
    url = "ftp://ftp.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aod_gridded/idps/snpp/edraot550/"
    file = f"npp_aot550_edr_gridded_0.25_{d_str}.high.bin"
    gz_file = file +".gz"
    link = url + d_str[:4] + "/" + gz_file
    gz_file_path = fr"{out_dir}/{gz_file}"
    file_path = fr"{out_dir}/{file}"
    try:
        if os.path.exists(gz_file_path):
            print(f"le fichier {gz_file_path} a déjà été téléchargé")
        else:
            with closing(request.urlopen(link)) as r:
                with open(gz_file_path, 'wb') as f:
                    # TODO Create condition of cloud cover and data availability over ROI
                    shutil.copyfileobj(r, f)
                    print("An image was found for this date : %s"%(d_str))

        with gzip.open(gz_file_path, 'rb') as f_zip:
            with open(file_path, 'wb') as f_dez:
                shutil.copyfileobj(f_zip, f_dez)
        
        file = File(file_path)
        start_date,end_date = file.getAcqDates()
        return file_path,start_date,end_date

    except EOFError:
        print("EOFError")
        return False
    