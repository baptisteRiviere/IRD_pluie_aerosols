from sentinelsat import SentinelAPI
from datetime import date, datetime, timedelta
import numpy.ma as ma
import numpy as np
import json
import sys
import os

sys.path.insert(0, r'Images')
from File import File
from Image import Image

sys.path.insert(0, r'tools')
from tools import make_directory

def download_S5AI_image(tg_date,download_dir,projection):
    year,month,day = tg_date.year,tg_date.month,tg_date.day
    llx,lly,urx,ury = projection["llx"],projection["lly"],projection["urx"],projection["ury"]
    api = SentinelAPI('s5pguest', 's5pguest', 'https://s5phub.copernicus.eu/dhus/')
    footprint = f"GEOMETRYCOLLECTION(POLYGON(({llx} {lly},{llx} {ury},{urx} {ury},{urx} {lly},{llx} {lly})))"
    products = api.query(footprint, date=(date(year,month,day), date(year,month,day+1)), producttype='L2__AER_AI', platformname='Sentinel-5')
    filenames = [download_dir+"/"+products[k]["filename"] for k in products.keys()]
    str_tg_date = datetime.strftime(tg_date,"%Y%m%d")
    tiff_filename = fr"{download_dir}/Sentinel5_mean_{str_tg_date}.tif"
    if os.path.exists(tiff_filename):
        print(f"S5AI : le fichier a déjà été téléchargé pour la date {tg_date}")
        start_date = datetime(year=year,month=month,day=day)
        return tiff_filename,start_date,start_date+timedelta(days=1)
    elif len(filenames) == 0 or os.path.exists(filenames[0]):
        print(f"S5AI : aucun fichier n'a pu être obtenu pour la date {tg_date}")
        return False
    else:
        print(f"S5AI : téléchargement de {len(filenames)} fichier(s) pour la date {tg_date}")
        api.download_all(products,download_dir,checksum=False)
        try:
            images = [File(fn).project(projection,"aerosol_index_354_388") for fn in filenames]
            mean_arrays = ma.array([img.array for img in images]).mean(axis=0)
            img = Image(mean_arrays,images[0].lons,images[0].lats)
            img.save(projection,tiff_filename)
            acq_dates = [File(fn).getAcqDates() for fn in filenames]
            start_date,end_date = np.min(acq_dates,axis=0)[0],np.max(acq_dates,axis=0)[1]
            return tiff_filename, start_date, end_date
        except Exception as e:
            print(f"une erreur est survenue pour la date {tg_date} :\n{e}")
            return False

if __name__ == "__main__":
    
    directory_path = make_directory(r"../data/Sentinel5_UVAI")
    projection_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

    tg_date = datetime(year=2018,month=8,day=5,hour=12)
    result = download_S5AI_image(tg_date,directory_path,projection)
    attribute = "aerosol_index_354_388"
    if result != False:
        fn,sd,ed = result
        File(fn).getImage(1).show()

