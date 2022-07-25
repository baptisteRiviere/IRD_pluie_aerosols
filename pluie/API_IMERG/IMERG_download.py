
import requests
from datetime import datetime,timezone,timedelta
import os
import sys

sys.path.insert(0, r'Images')
from File import File

def download_IMERG_image(tg_date,download_dir):
    # Do not forget to add .netrc file in the root dir of Colab. printing `result` should return status code 200
    str_date = datetime.strftime(tg_date,"%Y%m%d")
    URL_root = f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDF.06/{str_date[:4]}/{str_date[4:6]}"
    fn = f"3B-DAY.MS.MRG.3IMERG.{str_date}-S000000-E235959.V06.nc4"
    precision = ".nc4?precipitationCal[0:0][1242:1300][915:974],HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974],nv"
    URL = f"{URL_root}/{fn}{precision}"
    full_fn = fr"{download_dir}/{fn}"
    result = requests.get(URL)
    if os.path.exists(full_fn):
        print(f"IMERG : le fichier a déjà été téléchargé pour la date {tg_date}")
    else:
        print(f"IMERG : téléchargement du fichier pour la date {tg_date}")
        result = requests.get(URL)
        try:
            result.raise_for_status()
            with open(full_fn, 'wb') as f:
                f.write(result.content)
        except:
            print('IMERG : requests.get() returned an error code '+str(result.status_code))
            return False
    start_date = datetime(year=tg_date.year,month=tg_date.month,day=tg_date.day,hour=0,minute=0,tzinfo=timezone.utc)
    end_date = start_date + timedelta(days=1)
    return full_fn,start_date, end_date

if __name__ == "__main__":
    dir = r"../data/IMERG"
    d = datetime(year=2020,month=12,day=1)
    fn = download_IMERG_image(d,dir)
    file = File(fn)
    img = file.getImage("HQprecipitation")
    img.show()
    

