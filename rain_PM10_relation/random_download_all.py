import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
from datetime import datetime
import sys
import json
import random
from API_sentinel5 import download_S5AI_image

sys.path.insert(0, r'tools')
from tools import make_directory, save_index, get_index

sys.path.insert(0, r'Images')
from File import File

sys.path.insert(0, r'pluie/API_IMERG')
from IMERG_download import download_IMERG_image

sys.path.insert(0, r'pluie')
import ground_truth_rain as gtr


def acquire_data(gt_AOT_path,gt_rain_path,index_path):
    """
    Télécharge et met en place les différentes données (Sentinel 5 AI, IMERG, vérité terrain AOT, vérité terrain pluie) pour les dates 
    """
    index = get_index(index_path)
    gt_AOT_df = pd.read_excel(gt_AOT_path)
    gt_rain_dict = gtr.csv2dict(gt_rain_path,quiet=True)[0]
    rows_2019 = [row for index,row in gt_AOT_df.iterrows() if row["Date"].year == 2019]
    random.seed(44)
    random.shuffle(rows_2019)
    for row in rows_2019:
        d = row["Date"] ; d_str = datetime.strftime(d,"%Y-%m-%d")
        if d_str not in index.keys():
            result_S5AI = download_S5AI_image(d,S5_dir,projection)
            if (result_S5AI!=False):
                result_IMERG = download_IMERG_image(d,IMERG_dir)
                if (result_IMERG!=False):
                    index[d_str] = {}
                    file_S5AI = File(result_S5AI[0])
                    fn_IMERG,start_date_IMERG,end_date_IMERG = result_IMERG
                    gt_rain_dict_extr = gtr.extract(gt_rain_dict,start_date_IMERG,end_date_IMERG)
                    gt_rain_dict_agreg = gtr.agreg(gt_rain_dict_extr,timedelta=False,method="mean")
                    file_IMERG = File(fn_IMERG)
                    index[d_str]["gt_AOT_cay"]      = row["Cayenne"]
                    index[d_str]["gt_rain_cay"]     = gt_rain_dict_agreg[list(gt_rain_dict_agreg.keys())[0]][3]
                    index[d_str]["path_S5AI"]       = result_S5AI[0]
                    index[d_str]["path_IMERG"]      = result_IMERG[0]
                    index[d_str]["value_S5AI_cay"]  = file_S5AI.getPxlValue(4.933351,-52.310793)
                    index[d_str]["value_IMERG_cay"] = file_IMERG.getPxlValue(4.933351,-52.310793,"HQprecipitation")
                save_index(index,index_path)
                
    

if __name__ == "__main__":
    AOT_path = r"../data/pic_mean_AOT/tableau_pics_mean_AOT_sup_50.xlsx"
    rain_path = r"../data/pluie_sol/gg_2019_1h.csv"

    VIIRS_dir = make_directory(r"../data/VIIRS_AOT")
    S5_dir = make_directory(r"../data/Sentinel5_UVAI")
    IMERG_dir = make_directory(r"../data/IMERG")

    projection_path = r"../data/param_proj/param_guy.json"
    projection = json.load(open(projection_path, "r", encoding="utf-8"))

    index_path = r"../data/index.json"

    acquire_data(AOT_path,rain_path,index_path)