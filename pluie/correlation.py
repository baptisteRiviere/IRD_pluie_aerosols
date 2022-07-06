# importing librairies
import matplotlib.pyplot as plt
import json
import numpy as np
from datetime import datetime
import sys
from scipy.stats import pearsonr, spearmanr
import warnings

# importing RACC modules
import ground_truth as gt

# importing modules from Images
sys.path.insert(0, r'../Images')
from Image import Image
from File import File
from Geotiff_Format import Geotiff_Format




def correl_TB_MO_IR(path_dates,key1,key2,projection=False,savefig=False):
    warnings.simplefilter("ignore")
    dates = get_dates(path_dates)
    arrays_1, arrays_2 = np.array([]),np.array([])
    for d in dates.keys(): # récupération des images
        file1 , file2 = File(dates[d][key1]), File(dates[d][key2])
        if projection:
            img1 = file1.project("temporary.tiff",projection,1)
            img2 = file2.project("temporary.tiff",projection,1)
        else:
            img1 = File(dates[d][key1]).getImage(1)
            img2 = File(dates[d][key2]).getImage(1)
        arrays_1 = np.append(arrays_1,img1.array.flatten())
        arrays_2 = np.append(arrays_2,img2.array.flatten())
        break
    
    corr, _ = pearsonr(arrays_1, arrays_2)
    plt.scatter(arrays_1,arrays_2)
    if projection:
        zone = projection["area_id"]
        plt.title(f"corr Pearson {key1} et {key2} à {zone}: {round(corr,3)}")
    else :
        plt.title(f"corr Pearson {key1} et {key2} : {round(corr,3)}")
    plt.xlabel(f"température de brillance {key1} en K")
    plt.ylabel(f"température de brillance {key2} en K")
    if savefig:
        plt.savefig(savefig, dpi=500)


def correl_rr_gt(path_dates,path_GT,path_metadata_GT,format="%Y-%m-%dT%H:%M:%S.%f%z",rr_key="rain_rate",indice_corr="Pearson",savefig=False):
    """
    Calcule la corrélation de Pearson entre les mesures de pluie estimées par les images SSMIS et les mesures sur le terrain
    """
    # récupération des fichiers
    gt_dict = gt.csv2dict(path_GT)[0]
    metadata_gt = gt.get_metadata(path_metadata_GT)
    dates = get_dates(path_dates)
    # initialisation des listes contenant les données dont on va calculer la corrélation
    estim_rain, true_rain, loc = [], [], []
    for d in dates.keys(): 
        if "*" in rr_key:
            for pola in ["V","H"]:
                try:
                    img = File(dates[d][rr_key.replace("*",pola)]).getImage(1)
                    break
                except KeyError:
                    pass
        else:
            img = File(dates[d][rr_key]).getImage(1)
        start_date_string,end_date_string = dates[d]["SSMIS_acq_start"],dates[d]["SSMIS_acq_end"]
        start_date,end_date = datetime.strptime(start_date_string,format),datetime.strptime(end_date_string,format)
        extr_gt_dict = gt.extract(gt_dict,start_date,end_date)
        agr_gt_dict = gt.agreg(extr_gt_dict)
        agr_gt = np.array([agr_gt_dict[d] for d in agr_gt_dict.keys()])
        for k in metadata_gt.keys():
            lat, lon = float(metadata_gt[k]["lat"]),float(metadata_gt[k]["lon"])
            lats, lons = img.lats.T[0], img.lons[0]
            idx_lat,idx_lon = (np.abs(lats - lat)).argmin(), (np.abs(lons - lon)).argmin()
            estimated_rain = img.array[idx_lat][idx_lon]
            if not np.isnan(estimated_rain):
                true_rain.append(agr_gt[0][k-1])
                estim_rain.append(estimated_rain)
                loc.append(metadata_gt[k]["Nom"])
    
    if indice_corr == "Pearson":
        corr, _ = pearsonr(estim_rain, true_rain)
    elif indice_corr == "Spearman":
        corr, _ = spearmanr(estim_rain, true_rain)

    
    plt.scatter(true_rain,estim_rain)
    plt.title(f"indice de corrélation de {indice_corr}: {round(corr,3)}")
    plt.xlabel("pluviommétrie accumulée sur la période d'acquisition, vérité terrain en mm")
    plt.ylabel("température de brillance acquis par SEVIRI à 830 nm en K")
    if savefig:
        plt.savefig(savefig, dpi=500)



if __name__ == "__main__":
    gt_fn = r"../../data/pluie_sol/gg_12-20_6m.csv"
    mtd_fn = r"../../data/pluie_sol/gauges_guyane_metadata.csv"

    proj_st_geo = r"../../data/param_proj/param_St_Georges.json"
    proj_st_lau = r"../../data/param_proj/param_St_Laurent.json"
    proj_test = r"../../data/param_proj/test.json"
    param_proj = json.load(open(proj_st_lau, "r", encoding="utf-8"))

    savefig = r"../../rapports/images/correlation_TB_IR_MO_guy.png"

    correl_TB_MO_IR(path_dates,"SSMIS_91V","IR_087",savefig=savefig)


    #correl_rr_gt(path_dates,gt_fn,mtd_fn,rr_key="IR_087",indice_corr="Spearman",savefig=savefig)