import numpy as np
from datetime import datetime,timedelta,timezone
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import unicodedata

def csv2dict(filename):
    out_dict = {} ; format = "%Y-%m-%d %H:%M:%S"
    with open(filename, mode="r") as pluies:
        csvreader = csv.reader(pluies)
        header = next(csvreader)
        counter = 0
        for row in csvreader:
            try:
                date = datetime.strptime(row[0],format)
                out_dict[date] = np.array([float(x) for x in row[1:]])
            except IndexError: 
                counter += 1
        if counter > 0:
            print(f"{counter} lignes ont été écartées, il s'agit probablement de lignes vides")
    return out_dict,header

def dict2csv(in_dict,out_filename,header=False):
    format = "%Y-%m-%d %H:%M:%S"
    with open(out_filename, 'w') as f: 
        write = csv.writer(f)
        if header:
            write.writerow(header)
        liste = [[datetime.strftime(k,format)]+list(in_dict[k]) for k in in_dict.keys()]
        write.writerows(liste)

def get_metadata(filename):
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

    for acq_date in in_dict.keys():
        acq_date_utc = acq_date.replace(tzinfo=timezone.utc)
        if start_date_utc < acq_date_utc < end_date_utc:
            out_dict[acq_date] = in_dict[acq_date]

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
    dates = list(in_dict.keys())
    start_dt, end_dt = dates[0],dates[-1]
    
    if timedelta:
        period = end_dt - start_dt
        nb_iter = int(period.total_seconds()/timedelta.total_seconds())
        new_dates = [start_dt + i*timedelta for i in range(nb_iter)]
    else :
        new_dates = [start_dt]
    
    #new_rain = {d:np.zeros(in_dict[d].shape) for d in new_dates}
    data_per_date = {d:[] for d in new_dates}
    
    for d in dates:
        left_nd, min = new_dates[0],(d-new_dates[0]).total_seconds()
        for nd in new_dates:
            delta = (d-nd).total_seconds()
            if (0 <= delta < min):
                left_nd, min = nd, delta
        data_per_date[left_nd] = data_per_date[left_nd] + [list(in_dict[d])]

    np_method = {"sum":np.sum,"mean":np.mean}
    new_rain = {d:np_method[method](np.array(data_per_date[d]),axis=0) for d in data_per_date.keys()}

    return new_rain
    

if __name__ == '__main__':
    format = "%Y-%m-%d %H:%M:%S"
    src_fn = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"
    extr_fn = r"../data/pluie_sol/gg_12-20_6m.csv"
    agr_fn_1j = r"../data/pluie_sol/gg_12-20_1j.csv"
    agr_fn_1h = r"../data/pluie_sol/gg_12-20_1h.csv"
    mtd_fn = r"../data/pluie_sol/gauges_guyane_metadata.csv"
    start_date, end_date = "2020-12-01 00:00:00","2020-12-31 00:00:00"

    agr_test = r"../data/pluie_sol/gg_test.csv"
    
    plot(agr_fn_1j,[2,4,5,6,7],mtd_fn,title="mesures de pluies au sol par jour en décembre 2020")
    #plot(agr_fn_1h,[4,5,6,7],mtd_fn,title="mesures de pluies au sol par heure en décembre 2020")

