import glob as glob
from File import File
from Image import Image
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as pil
import netCDF4 as nc
import datetime

projection_path = r"Images/param_guy.json"
projection = json.load(open(projection_path, "r", encoding="utf-8"))

def search(dir,projection,tg_date="*",freq="*",pola="*"):
    year = str(tg_date.year)
    days = (tg_date - datetime.datetime.strptime(year,"%Y")).days # TODO voir comment enlever le +1
    delta_min, fn_min = np.iinfo(np.int32).max, None
    for offset in [-1,0,1]:
        fns = glob.glob(dir+ rf"/*/*{year}{days+offset}-{freq}{pola}-*.nc")
        for fn in fns:
            file = File(fn)
            acq_date = file.getTime(projection,"TB_time").replace(tzinfo=None)
            img = file.project(r"../data/test.tiff",projection,"TB")
            delta = (tg_date-acq_date).total_seconds()
            try :
                unique, counts = np.unique(img.array, return_counts=True)
                zero_rate = dict(zip(unique, counts))[0]/(img.array.shape[0]*img.array.shape[1])
            except KeyError:
                zero_rate = 0
            print(acq_date, zero_rate)
            if (zero_rate < 0.1) and (np.abs(delta) < delta_min):
                delta_min, fn_min = delta, fn
    file = File(fn_min)
    return file, file.getTime(projection,"TB_time")


date = datetime.datetime.strptime("21/12/20 16:30", "%y/%m/%d %H:%M") ; freq = 91 ; pola = "*"
file,acq_time = search("../data/SSMI/download_dec_2021",projection,date,freq,pola)
print(acq_time)

"""
for fn in fns:
    file = File(fn)
    img = file.getImage("TB")
    plt.imshow(img.array)
    plt.show()
    date=fn.split("-")[-6]
    #img = file.project(rf"../data/SSMI/19V/SSMI_19V_{date}.tiff",projection,"TB")


SSMI_19V = glob.glob(r"../data/SSMI/19V/*.tiff")
SSMI_37V = glob.glob(r"../data/SSMI/37V/*.tiff")

dates_19V = {SSMI_19V[i][-12:-5]:SSMI_19V[i] for i in range(len(SSMI_19V))}
dates_37V = {SSMI_19V[i][-12:-5]:SSMI_37V[i] for i in range(len(SSMI_37V))}

dates_com = list(set(dates_19V.keys()).intersection(dates_37V.keys()))

paires = {dates_com[i]:{"19V":dates_19V[dates_com[i]], "37V":dates_37V[dates_com[i]]} for i in range(len(dates_com))}

date = "2021335"
TB19v = File(paires[date]["19V"]).getImage(1).array
TB37v = File(paires[date]["37V"]).getImage(1).array

#TB19v = File(r"../data/SSMI/37V\SSMI_19V_2021335.tiff").getImage(1).array
#TB37v = File(r"../data/SSMI/37V\SSMI_37V_2021335.tiff").getImage(1).array

TB19v = np.array(pil.open(r"../data/SSMI/19V\SSMI_19V_2021335.tiff"))
TB37v = np.array(pil.open(r"../data/SSMI/37V\SSMI_37V_2021335.tiff"))

R = np.exp(-17.76849 - 0.09612*TB37v + 0.15678*TB19v) -1.0
R = np.where(np.abs(R)<30,R,np.nan)
plt.imshow(R)
plt.show()

lons, lats = File(paires[date]["19V"]).getImage(1).lons, File(paires[date]["19V"]).getImage(1).lats

img = Image(R*1000,lons,lats)
img.save(projection,r"../data/SSMI/rain_rate.tiff")
#0.125


"""


