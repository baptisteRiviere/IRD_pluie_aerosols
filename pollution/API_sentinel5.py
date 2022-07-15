from sentinelsat import SentinelAPI
from datetime import date, datetime
import numpy.ma as ma
import numpy as np
import json
import sys
import os

sys.path.insert(0, r'Images')
from File import File
from Image import Image

def download_S5_image(tg_date,download_dir,projection):
    year,month,day = tg_date.year,tg_date.month,tg_date.day
    llx,lly,urx,ury = projection["llx"],projection["lly"],projection["urx"],projection["ury"]
    api = SentinelAPI('s5pguest', 's5pguest', 'https://s5phub.copernicus.eu/dhus/')
    footprint = f"GEOMETRYCOLLECTION(POLYGON(({llx} {lly},{llx} {ury},{urx} {ury},{urx} {lly},{llx} {lly})))"
    products = api.query(footprint, date=(date(year,month,day), date(year,month,day+1)), producttype='L2__AER_AI', platformname='Sentinel-5')
    filenames = [download_dir+"/"+products[k]["filename"] for k in products.keys()]
    if os.path.exists(filenames[0]):
        print(f"le fichier a déjà été téléchargé pour la date {tg_date}")
    else:
        api.download_all(products,download_dir)
    images = [File(fn).project(projection,"aerosol_index_354_388") for fn in filenames]
    arrays = ma.array([img.array for img in images])
    img = Image(arrays.mean(axis=0),images[0].lons,images[0].lats)
    str_tg_date = datetime.strftime(tg_date,"%Y%m%d")
    tiff_filename = fr"{download_dir}/Sentinel5_mean_{str_tg_date}.tiff"
    img.save(projection,tiff_filename)
    acq_dates = [File(fn).getAcqDates() for fn in filenames]
    start_date,end_date = np.min(acq_dates,axis=0)[0],np.max(acq_dates,axis=0)[1]
    return tiff_filename, start_date, end_date


if __name__ == "__main__":
    
    directory_path = r"../data/Sentinel5_AOT"
    projection_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

    tg_date = datetime(year=2020,month=12,day=5,hour=12)
    
    fn,sd,ed = download_S5_image(tg_date,directory_path,projection)
    print(fn)

    attribute = "aerosol_index_354_388"
