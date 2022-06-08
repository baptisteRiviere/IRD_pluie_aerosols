from matplotlib.font_manager import json_load
from File import File
import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from datetime import datetime
from Image import Image


def download_all(file,out_path):
    for att in file.getAttributes():
        #out_path_var = out_dir + f"{att}_var.tiff"
        image = file.project(out_path,projection,att)
        """
        if image : # if image != False
            image_var = image.computeVar()
            image_var.save(projection,out_path_var)
        """

def selection_dir(dir,projection,attribute,zero_rate=0.1):
    paths = glob.glob(dir + "*/*.nc")
    out_dict = {}
    for path in paths:
        file = File(path)
        image = file.project("temporary.tiff",projection,attribute)
        arr = image.array
        try :
            unique, counts = np.unique(arr, return_counts=True)
            zero_rate = dict(zip(unique, counts))[0]/(arr.shape[0]*arr.shape[1])
        except KeyError:
            zero_rate = 0
        if zero_rate < 0.1:
            date = file.getTime(projection,f"{attribute}_time")
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            out_dict[date] = path
    with open(dir+"dates.json", 'w', encoding='utf-8') as f:
        json.dump(out_dict, f, ensure_ascii=False, indent=4)
    return out_dict



def download_SSMI(json_path,dates,projection):
    
    dates_dir = json.load(open(json_path, "r", encoding="utf-8"))
    
    for d in dates:
        filename = dates_dir[d]
        file = File(filename)
        day=d.split(" ")[0]
        file.project(rf"../data/RACC/train/SSMI_{day}.tiff",projection,"TB")
    

def download_IR(filenames,projection,attribute):
    for fn in filenames:
        file = File(fn)
        date = fn.split("-")[-2]
        yyyy,mm,dd = date[:4],date[4:6],date[6:8]
        file.project(rf"../data/IR/agregation/{attribute}_{yyyy}-{mm}-{dd}.tiff",projection,attribute)
    """
    file = File(fn)
    download_all(file,r"../data/IR/results/IR{")
    """

def aggregation(dir,projection,mode="sum",variance=False):
    filenames = glob.glob(rf"{dir}*.tiff")
    images = []
    for fn in filenames:
        file = File(fn)
        images.append(file.getImage(1).array)
        lons,lats = file.getImage(1).lons, file.getImage(1).lats    # TODO : recalculer à chaque fois ? ce ne sont pas des manières
    if mode == "mean":
        output = np.mean(np.array(images),axis=0)
    else:
        output = np.sum(np.array(images),axis=0)
    img_output = Image(output, lons, lats)
    img_output.save(projection,dir+rf"{mode}.tiff")
    if variance :
        img_output_var = img_output.computeVar()
        img_output_var.save(projection,dir+rf"{mode}_var.tiff")
    


    
if __name__ == "__main__":
    projection_path = r"Images/param_guy.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

    
    MO_file = File(r"../data/SSMI/NSIDC-0630-EASE2_N25km-F16_SSMIS-2021364-91V-E-GRD-CSU-v1.5.nc")
    IR_file = File(r"../data/IR/MSG4-SEVI-MSG15-0100-NA-20211230201243.081000000Z-NA.nat")
    out_dir = r"../data/RACC/all_data/"

    #download_all(MO_file,out_dir)
    #download_all(IR_file,out_dir)

    #download_SSMI(r"../data/SSMI/",projection,"TB")

    #download_IR(glob.glob(r"../data/IR/*.nat"),projection,"IR_087")

    #aggregation(r"../data/SSMI/agregation/",projection,"mean")
    aggregation(r"../data/IR/agregation/",projection,"mean",True)











    """
    dates = [
        "2021-11-30 10:11:07",
        "2021-12-01 20:00:54",
        "2021-12-03 22:17:15",
        "2021-12-04 22:03:37",
        "2021-12-12 21:57:28",
        "2021-12-13 21:44:29",
        "2021-12-22 20:24:51",
        "2021-12-25 21:50:50"
    ]
    download_SSMI_from_json(f"{dir}dates.json",dates,projection)
    """




    
    
    
    
    
    






"""
    #attributes = ['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073'] 
    attributes = ['IR_087']
    for att in attributes:
        out_path = rf"../data/test_seg/Meteosat_{att}.tiff"
        compute_var_path = rf"../data/test_seg/Meteosat_{att}_var.tiff"
        values = convert_nat(nat_path,out_path,proj_path,att,compute_var_path)

         for date in dates_dir.keys():
        dates_list.append(datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
    dates = matplotlib.dates.date2num(dates_list)
    y = [1 for i in range(len(dates_list))]
    plt.plot_date(dates,y)
    plt.show()

    
    dates_list = list(dates_dir.keys())
    dates_list.sort()
    print(dates_list)
    """

