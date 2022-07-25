import numpy as np
from datetime import datetime,timedelta,timezone
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import unicodedata
import pandas as pd

def csv2dict(filename,quiet=False):
    """
    conversion d'un fichier csv en dictionnaire à partir de son chemin d'accès

    Args:
        filename (string): chemin d'accès au fichier
        quiet (bool): indique si le programme doit afficher les messages d'avertissement (Default False)
    Return :
        out_dict (dict): dictionnaire contenant les données
        header (array): en tête du fichier
    """
    out_dict = {} ; format = "%Y-%m-%d %H:%M:%S"
    with open(filename, mode="r") as pluies:
        csvreader = csv.reader(pluies)
        header = next(csvreader)
        counter = 0
        for row in csvreader:
            try:
                date = datetime.strptime(row[0],format)
                for i in range(len(row)):
                    if row[i] == '':
                        row[i] = np.NaN
                out_dict[date] = np.array([float(x) for x in row[1:]])
            except IndexError: 
                counter += 1
        if counter > 0 and (not quiet):
            print(f"{counter} lignes ont été écartées, il s'agit probablement de lignes vides")
    return out_dict,header

def dict2csv(in_dict,out_filename,header=False):
    """
    conversion d'un dictionnaire en fichier csv

    Args:
        in_dict (dict): dictionnaire contenant les données
        out_filename (string): chemin d'accès au fichier
        header (array): en tête du fichier (Default False)        
    """
    format = "%Y-%m-%d %H:%M:%S"
    with open(out_filename, 'w') as f: 
        write = csv.writer(f)
        if header:
            write.writerow(header)
        liste = [[datetime.strftime(k,format)]+list(in_dict[k]) for k in in_dict.keys()]
        write.writerows(liste)

def get_metadata(filename):
    """
    convertion des métadonnées en dictionnaire

    Args:
        filename (string): chemin d'accès au fichier contenant les métadatas
    Return:
        metadata (dict): dictionnaire contenant les métadonnées
    """
    metadata = {}
    with open(filename, mode="r", encoding="UTF-8") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        i=1
        for row in csvreader:
            metadata[i] = {header[i]:unicodedata.normalize("NFKD", row[i]) for i in range(len(header))}
            i+=1
    return metadata

def extract(in_dict,start_date_utc,end_date_utc):
    out_dict = {}
    tg_date_utc = start_date_utc + timedelta(seconds=(end_date_utc-start_date_utc).total_seconds())
    
    nearest_acq_date = list(in_dict.keys())[0]
    nb_rows = len(list(in_dict.keys()))
    i = 0
    for acq_date in in_dict.keys():
        acq_date_utc = acq_date.replace(tzinfo=timezone.utc)
        if start_date_utc <= acq_date_utc <= end_date_utc:
            out_dict[acq_date] = in_dict[acq_date]
        if abs((acq_date_utc - tg_date_utc).total_seconds()) < abs((nearest_acq_date.replace(tzinfo=timezone.utc) - tg_date_utc).total_seconds()):
            nearest_acq_date = acq_date

    if len(out_dict.keys()) == 0:
        print("il n'existe pas de données dans la plage temporelle en entrée, le dictionnaire en sortie ne contient que la date la plus proche")
        out_dict[nearest_acq_date] = in_dict[nearest_acq_date]
    
    return out_dict

def plot(filename,cols,metd_fn=False,title=False):
    if metd_fn:
        metadata = get_metadata(metd_fn)
    else:
        metadata = {col:{'Nom':str(col)} for col in cols}
    
    rain = csv2dict(filename)[0]
    
    dates = [list(rain.keys()) for col in cols]
    rain_data = [[rain[d][col-1] for d in dates[0]] for col in cols]

    fig, ax = plt.subplots(ncols=1)
    
    if title:
        fig.suptitle(title)
    
    for i in range(len(cols)):
        ax.plot_date(dates[i], rain_data[i], markersize=3, linestyle='solid')

    locator = mdates.AutoDateLocator()
    
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.legend([metadata[col]['Nom'] for col in cols])
    fig.autofmt_xdate()
    ax.set_ylabel('accumulation de pluie sur la période (mm)')
    
    plt.show()

def agreg(in_dict,timedelta=False,method="sum"):
    """
    rain_df = pd.read_csv(in_fn)
    if method == "sum":
        rain_df.resample(timedelta).sum()
    elif method == "mean":
        rain_df.resample("5Min").mean()
    return rain_df

    """
    dates = list(in_dict.keys())
    i = 0
    if len(dates) == 1:
        print("il n'existe qu'une seule date, impossible d'agréger ces données")
        return in_dict

    start_dt, end_dt = dates[0],dates[-1]
    if timedelta:
        period = end_dt - start_dt
        nb_iter = int(period.total_seconds()/timedelta.total_seconds())
        new_dates = [start_dt + i*timedelta for i in range(nb_iter)]
    else :
        new_dates = [start_dt]
    
    data_per_date = {d:[] for d in new_dates}
    nb_rows = len(dates)
    for d in dates:
        left_nd, min = new_dates[0],(d-new_dates[0]).total_seconds()
        for nd in new_dates:
            delta = (d-nd).total_seconds()
            if (0 <= delta < min):
                left_nd, min = nd, delta
        data_per_date[left_nd] = data_per_date[left_nd] + [list(in_dict[d])]
        i += 1
        if i % 50 == 0:
            print(f"{i}/{nb_rows}")

    np_method = {"sum":np.nansum,"mean":np.nanmean}
    new_rain = {d:np_method[method](np.array(data_per_date[d]),axis=0) for d in data_per_date.keys()}

    return new_rain
    

if __name__ == '__main__':
    format = "%Y-%m-%d %H:%M:%S"
    fn_6min = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"
    fn_1h = r"../data/pluie_sol/gg_1h.csv"
    fn_1j = r"../data/pluie_sol/gg_1j.csv"
    extr_fn_6m = r"../data/pluie_sol/gg_2013-2020_6m.csv"
    agr_fn_1j = r"../data/pluie_sol/gg_2013-2020_1j.csv"
    metd_fn = r"../data/pluie_sol/gauges_guyane_metadata.csv"
    start_date = datetime.strptime("2013-01-01 00:00:00",format).replace(tzinfo=timezone.utc)
    end_date = datetime.strptime("2020-12-31 23:59:00",format).replace(tzinfo=timezone.utc)




    # extraction pour la période d'intéret
    #src_dict,header = csv2dict(src_fn) 
    #extr_6m_dict = extract(src_dict,start_date,end_date)
    #dict2csv(extr_6m_dict,extr_fn_6m,header=header)

    #extr_6m_dict,header = csv2dict(extr_fn_6m)
    #plot(extr_fn_6m,cols=[1,2,3,4,5,6],metd_fn=metd_fn)

    """
    rain_df = pd.read_csv(fn_6min)
    rain_df['time'] = pd.to_datetime(rain_df['time'])
    rain_1h_df = rain_df.resample('60min', on='time').mean()
    rain_1h_df.to_csv(fn_1h)
    """

    fn_1h = r"../data/pluie_sol/gg_2013-2020_1h.csv"
    rain_1h_df = pd.read_csv(fn_1h)
    rain_1h_df['time'] = pd.to_datetime(rain_1h_df['time'])
    rain_1j_df = rain_1h_df.resample('D', on='time').sum()
    rain_1j_df.to_csv(fn_1j)
    print(rain_1j_df)
    
    

    #agr_1h_dict = agreg(extr_6m_dict,timedelta=timedelta(hours=1),method="sum")
    #dict2csv(agr_1h_dict,agr_fn_1h,header=header)

    #agr_1h_dict,header = csv2dict(agr_fn_1h)
    #plot(agr_fn_1h,cols=[1,2,3,4,5,6,7],metd_fn=metd_fn)

    #agr_1j_dict = agreg(agr_1h_dict,timedelta=timedelta(days=1),method="mean")
    #dict2csv(agr_1j_dict,agr_fn_1j,header=header)
    #plot(agr_fn_1j,cols=[1,2,3,4,5,6],metd_fn=metd_fn)
    
    #agr_1j_dict,header = csv2dict(agr_fn_1j)
    #plot(agr_fn_1j,cols=[1,2,3,4,5,6,7],metd_fn=metd_fn)