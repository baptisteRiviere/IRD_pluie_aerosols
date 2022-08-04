from cv2 import Subdiv2D_PREV_AROUND_RIGHT
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys
from datetime import datetime, timedelta, date
from scipy.stats import pearsonr
sys.path.insert(0, r'pluie')
import skccm as ccm
from skccm.utilities import train_test_split
from scipy.fft import fft, fftfreq




def join_rain_PM10(rain_path):
    rain_df = pd.read_csv(rain_path)                                    # lecture du csv
    rain_df['date'] = pd.to_datetime(rain_df['time'])                   # conversion de la colonne time en date 
    rain_df = rain_df.resample('D',on='date').sum()                     # agregation des données à la journée
    
    result_df = pd.DataFrame()
    
    for year in [y for y in range(2010,2021)]:
        PM10_path = rf"../data/PM10/Donnees_PM10_{year}.xlsx"           # nom du fichier PM10
        PM10_df = pd.read_excel(PM10_path,skiprows=[1,2])               # lecture du fichier
        PM10_df['date'] = pd.to_datetime(PM10_df['Date'])               # conversion de la date
        PM10_df = PM10_df.resample('D', on='date').mean()               # rééchantillonage : moyenne quotidienne
        cay_colname = PM10_df.columns[np.argmax(["cay" in col.lower() for col in PM10_df.columns])]
                                                                        # recherche du nom de colonne renvoyant à Cayenne
        # fusion des deux tableaux sur l'année et harmonisation
        part_result_df = pd.concat([PM10_df[[cay_colname]], rain_df["97307001"]], axis=1, join="inner")
        part_result_df = part_result_df.rename(columns={cay_colname: "PM10", "97307001": "rain"})
        part_result_df = part_result_df.fillna(0)    
        # pour conserver la périodicité : remplacement NaN par valeurs nulles
        # elles seront moyennées dans la DSP de Welsh
        
        # ajout au tableau final
        result_df = pd.concat([result_df,part_result_df])

    # sauvegarde du fichier
    result_df.to_csv(r"../data/coherence/PM10_pluie_2010-2020.csv")
    return result_df

def coherence(PM10_array,rain_array):
    freq = 1
    nbelem = len(PM10_array)

    f, Cxy = signal.coherence(PM10_array,rain_array,fs=freq,nperseg=2000)
    f_ = f/(60*60*24)
    Cxy_ = np.sqrt(Cxy)

    print(f"frequence\t= {freq}")
    print(f"nb_elem\t\t= {nbelem}")
    print(f"np_points\t= {len(Cxy)}")
    print(f"corr_max\t= {np.max(Cxy)}")
    
    #plt.semilogx(f_, Cxy_)
    plt.axhline(y = 0.15, color = 'r', linestyle = '-')
    plt.plot(f_, Cxy)
    plt.grid()
    plt.title("fonction de cohérence entre concentration de PM10 et pluviométrie")
    plt.xlabel('fréquence [Hz]')
    plt.ylabel('cohérence')
    plt.show()



def ondelettes(PM10_array,rain_array):
    a = len(PM10_array)//10
    widths = np.arange(1, a)
    cwtmatr = signal.cwt(rain_array, signal.morlet(w=6), widths)
    plt.imshow(np.abs(cwtmatr), extent=[-len(PM10_array)/2, len(PM10_array)/2, a, 1], aspect='auto')
    #vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max()
    plt.show()

def conv_cross_map(list1,list2,list1name="list 1",list2name="list 2"):
    lag = 5
    embed = 3
    
    # intégration
    e1 = ccm.Embed(list1)
    e2 = ccm.Embed(list2)
    X1 = e1.embed_vectors_1d(lag,embed)
    X2 = e2.embed_vectors_1d(lag,embed)

    #split the embedded time series
    x1tr, x1te, x2tr, x2te = train_test_split(X1,X2, percent=.75)

    CCM = ccm.CCM() #initiate the class

    #library lengths to test
    len_tr = len(x1tr)
    lib_lens = np.arange(50, len_tr, len_tr/50, dtype='int')

    #test causation
    CCM.fit(x1tr,x2tr)
    x1p, x2p = CCM.predict(x1te, x2te,lib_lengths=lib_lens)

    sc1,sc2 = CCM.score()

    fig, ax = plt.subplots(ncols=1)
    ax.plot(lib_lens,sc1, markersize=3, linestyle='solid')
    ax.plot(lib_lens,sc2, markersize=3, linestyle='solid')
    ax.legend([list1name,list2name])

    ax.set_ylabel('R²')
    ax.set_xlabel('taille de la librairie')
    
    plt.show()

def correlation(list1,list2,list1name="list 1",list2name="list 2"):
    
    corr, _ = pearsonr(list1, list2)
    #RMSE = np.sqrt(np.sum((ground_list-estim_list)**2)/len(ground_list))
    #BIAS = np.sum(estim_list-ground_list) / np.sum(ground_list)

    print(f"CC PEARSON = {round(corr,3)}")

    plt.scatter(list1,list2,s=50,alpha=0.8)
    plt.grid()
    plt.show()

    return corr

def plot(dates,list1,list2,list1name="list 1",list2name="list 2"):
    fig, ax = plt.subplots(ncols=1)
    ax.plot_date(dates, list1, markersize=3, linestyle='solid')
    ax.plot_date(dates, list2, markersize=3, linestyle='solid')
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.legend([list1name,list2name])
    fig.autofmt_xdate()
    ax.set_xlabel('date')
    plt.show()

if __name__ == "__main__":
    rain_path = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"         # chemin du fichier pluie
    #join_rain_PM10(rain_path)
    
    
    df = pd.read_csv(r"../data/coherence/PM10_pluie_2010-2020.csv")
    df['date'] = pd.to_datetime(df['date'],utc=True)
    PM10_array = np.array(df["PM10"].array) ; rain_array = df["rain"].array ; dates = df["date"]

    #coherence(PM10_array,rain_array)

    #correlation(PM10_array,rain_array)

    conv_cross_map(PM10_array,rain_array,"PM10 -> pluie","pluie -> PM10")
    
    #plot(dates,PM10_array,rain_array,"PM10 (μg/m³)","pluie (mm/jour)")

    """
    N = len(PM10_array)
    yf = fft(PM10_array)
    xf = fftfreq(N)[:N//2]
    plt.plot(xf, np.abs(yf[0:N//2]))
    plt.grid()
    plt.show()
    """