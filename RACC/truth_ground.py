import numpy as np
from datetime import datetime,timedelta
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO


def csv2dict(filename):
    rain = {} ; format = "%Y-%m-%d %H:%M:%S"
    with open(filename, mode="r") as pluies:
        csvreader = csv.reader(pluies)
        header = next(csvreader)
        for row in csvreader:
            date = datetime.strptime(row[0],format)
            rain[date] = np.array([float(x) for x in row[1:]])
    return rain,header

def dict2csv(dict,out_name,header=False):
    format = "%Y-%m-%d %H:%M:%S"
    with open(out_name, 'w') as f: 
        write = csv.writer(f)
        if header:
            write.writerow(header)
        liste = [[datetime.strftime(k,format)]+list(dict[k]) for k in dict.keys()]
        write.writerows(liste) 

def exctract(filename,out_name,start_date,end_date):
    format = "%Y-%m-%d %H:%M:%S"
    start_date,end_date = datetime.strptime(start_date,format),datetime.strptime(end_date,format)
    final_list = []
    with open(filename, mode="r") as pluies:
        csvreader = csv.reader(pluies)
        header = next(csvreader)
        for row in csvreader:
            acq_date = datetime.strptime(row[0],format)
            if start_date < acq_date < end_date:
                final_list.append(row)

    with open(out_name, 'w') as f: 
        write = csv.writer(f) 
        write.writerow(header) 
        write.writerows(final_list) 

def plot(filename,col=1):
    rain,header = csv2dict(filename)
    dates = list(rain.keys())
    rain_data = [rain[d] for d in dates]

    fig, ax = plt.subplots(1,1)
    ax.plot_date(dates, rain_data, markerfacecolor='CornflowerBlue', markeredgecolor='white')
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    fig.autofmt_xdate()
    plt.show()

def agreg(filename,out_name,timedelta=timedelta(hours=1)):
    rain,header = csv2dict(filename)
    dates = list(rain.keys())
    start_dt, end_dt = dates[0],dates[-1]
    period = end_dt - start_dt
    nb_iter = int(period.total_seconds()/timedelta.total_seconds())
    
    new_dates = [start_dt + i*timedelta for i in range(nb_iter)]
    new_rain = {d:np.zeros(rain[d].shape) for d in new_dates}
    for d in dates:
        min, near_d = np.iinfo(np.int32).max, new_dates[0]
        for new_d in new_dates:
            diff = abs((new_d-d).total_seconds())
            if diff < min:
                min, near_d = diff, new_d
        new_rain[near_d] = new_rain[near_d] + rain[d]
    dict2csv(new_rain,out_name,header=header)

if __name__ == '__main__':
    format = "%Y-%m-%d %H:%M:%S"
    src_fn = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"
    extr_fn = r"../data/pluie_sol/gauges_guyane_6min_utc_extracted_1.csv"
    agr_fn = r"../data/pluie_sol/gauges_guyane_6min_utc_extr_agr_days.csv"
    start_date, end_date = "2020-12-01 00:00:00","2020-12-31 00:00:00"
    
    #exctract(src_fn,extr_fn,start_date,end_date)
    plot(extr_fn)
    
    #agreg(extr_fn,agr_fn,timedelta=timedelta(days=1))





