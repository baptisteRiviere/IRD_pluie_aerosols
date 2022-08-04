
from tracemalloc import start
import requests
from datetime import datetime,timezone,timedelta
import os
import sys
import json

sys.path.insert(0, r'Images')
from File import File

def download_IMERG_image(tg_date,download_dir,mode="Final",quiet=False):
    # Do not forget to add .netrc file in the root dir of Colab. printing `result` should return status code 200
    str_date = datetime.strftime(tg_date,"%Y%m%d")
    URL_root = f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGD{mode[0]}.06/{str_date[:4]}/{str_date[4:6]}"
    if mode[0] == "F":
        fn = f"3B-DAY.MS.MRG.3IMERG.{str_date}-S000000-E235959.V06.nc4"
    else:
        fn = f"3B-DAY-L.MS.MRG.3IMERG.{str_date}-S000000-E235959.V06.nc4"
    precision = ".nc4?HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974],nv"
    URL = f"{URL_root}/{fn}{precision}"
    full_fn = fr"{download_dir}/{fn}"
    if os.path.exists(full_fn):
        if quiet == False:
            print(f"IMERG : le fichier a déjà été téléchargé pour la date {tg_date}")
    else:
        if quiet == False:
            print(f"IMERG : téléchargement du fichier pour la date {tg_date}")
        result_url = requests.get(URL)
        try:
            result_url.raise_for_status()
            with open(full_fn, 'wb') as f:
                f.write(result_url.content)
        except:
            if quiet == False:
                print('IMERG : requests.get() returned an error code '+str(result_url.status_code))
            return False
    start_date = datetime(year=tg_date.year,month=tg_date.month,day=tg_date.day,hour=0,minute=0,tzinfo=timezone.utc)
    end_date = start_date + timedelta(days=1)
    return full_fn,start_date,end_date

if __name__ == "__main__":
        
    dir = r"../data/IMERG/download"
    projection = json.load(open(r"../data/param_proj/param_guy_ext.json", "r", encoding="utf-8"))
    d = datetime(year=2022,month=4,day=4)
    dir_proj = r"C:\Users\Baptiste\Documents\ENSG\stage\data\analyses_pluie\images_IMERG_dates"
    result = download_IMERG_image(d,dir,mode="Late")
    if result != False:
        (fn,std,end) = result
        file = File(fn)
        str_d = datetime.strftime(d,'%Y-%m-%d')
        img = file.project(projection,"HQprecipitation")
        img.show()


# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.html
# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974]
# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220404-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1240:1291][912:966],time,lon[1240:1291],lat[912:966]