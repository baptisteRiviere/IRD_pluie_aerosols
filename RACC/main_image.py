from matplotlib.font_manager import json_load
from File import File
import json
import glob
import numpy as np
from Image import Image
import datetime


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

def aggregation(projection,out_name,images=[],dir=False,mode="mean"):
    if dir:
        images = []
        filenames = glob.glob(rf"{dir}*.tiff")
        for fn in filenames:
            file = File(fn)
            images.append(file.getImage(1).array)
            lons,lats = file.getImage(1).lons, file.getImage(1).lats
    if mode == "mean":
        output = np.mean(np.array(images),axis=0)
    else:
        output = np.sum(np.array(images),axis=0)
    img_output = Image(output, lons, lats)
    img_output.save(projection,out_name)
    
def search_near_SSMI(dir,projection,tg_date="*",freq="*",pola="*"):
    year = str(tg_date.year)
    days = (tg_date - datetime.datetime.strptime(year,"%Y")).days
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
            if (zero_rate < 0.1) and (np.abs(delta) < delta_min):
                delta_min, fn_min = delta, fn
    file = File(fn_min)
    return file, file.getTime(projection,"TB_time")

def prepare_data_RACC(main_dir,dates,projection):
    """
    sélectionne parmis les données SSMIS et IR les fichiers d'intérêt 
    télécharge ces fichiers puis les géoréférence de la même manière
    aggrège les données et calcule la variance des images IR
    """
    SSMI_imgs = []
    for date in dates:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") ; freq = 91 ; pola = "*"
        file,acq = search_near_SSMI("../data/SSMI/download_dec_2021",projection,dt,freq,pola)
        date_str = acq.strftime("%Y-%m-%d")
        img = file.project(rf"../data/RACC/produced/SSMIS_{date_str}.tiff",projection,"TB")
        SSMI_imgs.append(img.array)
    aggregation(projection,rf"../data/RACC/produced/SSMIS_agrege.tiff",SSMI_imgs)




if __name__ == "__main__":
    projection_path = r"Images/param_guy.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

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

    prepare_data_RACC(dir,dates,projection)
    

    #download_IR(glob.glob(r"../data/IR/*.nat"),projection,"IR_087")

    #aggregation(r"../data/SSMI/agregation/",projection,"mean")
    #aggregation(r"../data/IR/agregation/",projection,"mean",True)

    """
    
    dates_dir = json.load(open(r"../data/SSMI/dates.json", "r", encoding="utf-8"))
    
    for d in dates:
        filename = dates_dir[d].split("-")
        filename[-5] = "19V"
        f = '-'.join(filename)
        print(f)
    #download_SSMI_from_json(f"{dir}dates.json",dates,projection)
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

