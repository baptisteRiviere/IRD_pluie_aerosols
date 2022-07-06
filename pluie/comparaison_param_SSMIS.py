import glob
import json
import numpy as np
import sys
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import csv
from operator import itemgetter

sys.path.insert(0, r'RACC')
import ground_truth as gt

sys.path.insert(0, r'Images')
from Image import Image
from File import File


def append(dictionnary,key,true_rain,est_rain):
    if key in dictionnary.keys():
        rain_list = dictionnary[key]
    else :
        rain_list = [[],[]]
    true_rain_list = rain_list[0] + [true_rain]
    est_rain_list = rain_list[1] + [est_rain]
    rain_list = [true_rain_list,est_rain_list]
    dictionnary[key] = rain_list
    return dictionnary

def save_csv(data_path,gt_fn,mtd_fn,csv_filename,projection,attribute):
    gt_dict = gt.csv2dict(gt_fn)[0]
    metadata_gt = gt.get_metadata(mtd_fn)
    fns = glob.glob(data_path)
    rows=[]

    for fn in fns:
        [grid, capteur, date, freq, time_pass, algo, imput, version] = fn.split("NSIDC-0630-EASE2_")[-1].split("-")
        
        file = File(fn)
        img = file.project(projection,attribute)
        img_angle = file.project(projection,"Incidence_angle")

        try : # on compte les occurences de 0 pour déterminer si le fichier est corrompu
            unique, counts = np.unique(img.array, return_counts=True)
            zero_rate = dict(zip(unique, counts))[0]/(img.array.shape[0]*img.array.shape[1])
        except KeyError: # aucune occurence de 0
            zero_rate = 0

        if zero_rate < 0.1:
            incid_angle = np.mean(img_angle.array)
            try:
                start_date, end_date = file.getAcqDates()
                extr_gt_dict = gt.extract(gt_dict,start_date,end_date)
                print(extr_gt_dict)
                break
            except:
                pass
                """

                agr_gt_dict = gt.agreg(extr_gt_dict,method="mean")
                agr_gt = np.array([agr_gt_dict[d] for d in agr_gt_dict.keys()])
                for k in metadata_gt.keys():
                    lat, lon = float(metadata_gt[k]["lat"]),float(metadata_gt[k]["lon"])
                    lats, lons = img.lats.T[0], img.lons[0]
                    idx_lat,idx_lon = (np.abs(lats - lat)).argmin(), (np.abs(lons - lon)).argmin()
                    est_rain = img.array[idx_lat][idx_lon]
                    if not np.isnan(est_rain):
                        rows.append([capteur,grid,freq,time_pass,algo,incid_angle,str(agr_gt[0][k-1]),str(est_rain)])                     
            except IndexError:
                print(fn)
                print("index error")
                pass
            except KeyError:
                print(fn)
                print("key error")
                pass

    header = ["capteur","grid","freq","time_pass","algo","incidence","true_rain","est_rain"]
    with open(csv_filename, 'w') as f: 
        write = csv.writer(f,delimiter=',')
        write.writerow(header)
        write.writerows(rows)
    """

def get_csv(csv_filename):
    data = []
    with open(csv_filename, mode="r") as pluies:
        csvreader = csv.reader(pluies)
        header = next(csvreader)
        for row in csvreader:
            if row != []:
                row_dict = {header[i]:row[i] for i in range(len(row)-2)}
                row_dict["true_rain"] = float(row[-2])
                row_dict["TB"] = float(row[-1])
                data.append(row_dict)
    return data

def compare(data):
    capteur_list = ["F17_SSMIS","F16_SSMIS","F18_SSMIS"]
    grid_list = ["N3.125km","T3.125km","N25km","T25km"]
    freq_list = ["91H","91V"]
    pass_list = ["M","A","D","E"]
    algo_list = ["SIR","GRD"]

    result = []

    for freq in freq_list:
        for time_pass in pass_list:
            for algo in algo_list:
                for grid in grid_list:
                    for capteur in capteur_list:
                        true_rain_list, TB_list, angles = [],[],[]
                        for row in data:
                            if (row["capteur"] == capteur) and (row["grid"] == grid) and (row["freq"] == freq) and (row["time_pass"] == time_pass) and (row["algo"] == algo):
                                true_rain_list.append(row["true_rain"])
                                TB_list.append(row["TB"])
                                angles.append(float(row["incidence"]))
                        if len(TB_list) > 0:
                            corr, _ = spearmanr(TB_list, true_rain_list)
                            result.append([corr,abs(corr),len(TB_list),capteur,grid,freq,time_pass,algo,np.mean(angles)])
    
    result_sorted = sorted(result, key=itemgetter(1), reverse=True)
    with open(r"../data/result_corr_SSMIS.csv", 'w') as f: 
        write = csv.writer(f,delimiter=',')
        write.writerows(result_sorted)

if __name__ == "__main__":
    
    csv_filename = r"../data/recap_corr_SSMIS.csv"
    data_path = r"../data/SSMI/compa/*/*.nc"

    gt_fn = r"../data/pluie_sol/gg_12-20_1h.csv"
    mtd_fn = r"../data/pluie_sol/gauges_guyane_metadata.csv"

    attribute = "TB"
    projection = json.load(open(r"../data/param_proj/param_guy.json", "r", encoding="utf-8"))
    
    #save_csv(data_path,gt_fn,mtd_fn,csv_filename,projection,attribute)


    data = get_csv(csv_filename)
    # capteur,grid,freq,time_pass,algo,incidence,true_rain,est_rain


    for algo_etud in ["SIR","GRD"]:
        TB_list,rain_list = [],[]
        for row in data:
            capteur,incidence,freq,rain,TB,algo = row["capteur"],row["incidence"],row["freq"],row["true_rain"],row["TB"],row["algo"]
            if algo == algo_etud:
                TB_list.append(TB) ; rain_list.append(rain)
        corr, _ = spearmanr(TB_list, rain_list)
        print(algo_etud,len(TB_list),corr)



    

   





















"""
for dictionnary in [grid_dict, capteur_dict, freq_dict, time_pass_dict, algo_dict]:
    print("\n---------------------------")
    for key in dictionnary.keys():
        true_rain_list = dictionnary[key][0]
        est_rain_list = dictionnary[key][1]
        corr, _ = spearmanr(est_rain_list, true_rain_list)
        print(f"correlation pour {key} avec {len(est_rain_list)} points: {corr}")

print(count_zero)
corr, _ = spearmanr(estim_rain, true_rain)
print(corr)
print(len(true_rain))
plt.scatter(true_rain,estim_rain,s=30, alpha=0.8)
plt.show()

try : # on compte les occurences de 0 pour déterminer si le fichier est corrompu
        unique, counts = np.unique(img.array, return_counts=True)
        zero_rate = dict(zip(unique, counts))[0]/(img.array.shape[0]*img.array.shape[1])
    except KeyError: # aucune occurence de 0
        zero_rate = 0
"""