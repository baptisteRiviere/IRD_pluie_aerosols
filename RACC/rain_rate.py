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


