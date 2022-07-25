import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import datetime, timedelta, date
sys.path.insert(0, r'pluie')




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


if __name__ == "__main__":
    rain_path = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"         # chemin du fichier pluie
    #join_rain_PM10(rain_path)
    
    df = pd.read_csv(r"../data/coherence/PM10_pluie_2010-2020.csv")
    PM10_array = df["PM10"].array ; rain_array = df["rain"].array

    plt.scatter(PM10_array,rain_array)
    plt.show()

    freq = 1
    nbelem = len(PM10_array)

    f, Cxy = signal.coherence(PM10_array,rain_array,fs=freq,nperseg=100)
    f_ = f/(60*60*24)
    Cxy_ = np.sqrt(Cxy)

    print(f"frequence\t= {freq}")
    print(f"nb_elem\t\t= {nbelem}")
    print(f"np_points\t= {len(Cxy)}")
    print(f"corr_max\t= {np.max(Cxy)}")
    
    
    print(Cxy)
    #plt.semilogx(f_, Cxy_)
    plt.plot(f_, Cxy_)
    plt.grid()
    plt.xlabel('frequency [Hz]')
    #plt.xlim((10**-8,10**-5))
    plt.ylabel('Coherence')
    plt.show()

    """

    plt.plot(1/f,Cxy_)
    plt.grid()
    plt.xlabel('days')
    plt.ylabel('Coherence')
    plt.show()
    """





    """
    print(len(PM10_array),len(rain_array))
    corr = signal.correlate(PM10_array,rain_array,"same")
    plt.plot(corr)
    plt.show()

    Exy = np.fft.fft(signal.correlate(PM10_array,rain_array,"full"))
    Exx = np.fft.fft(signal.correlate(PM10_array,PM10_array,"full"))
    Eyy = np.fft.fft(signal.correlate(rain_array,rain_array,"full"))

    coh = np.sqrt(np.abs(Exy)**2/(Exx*Eyy))
    lags = signal.correlation_lags(len(PM10_array), len(rain_array), "full")
    F_lags = 1/lags
    print(len(F_lags))
    plt.plot(F_lags,np.abs(coh))
    #plt.xlim(10**-9,10**-5)
    plt.show()
    """
    

    """
    from scipy import signal
    import matplotlib.pyplot as plt
    rng = np.random.default_rng()

    fs = 10e3
    N = 1e5
    amp = 20
    freq = 1234.0
    noise_power = 0.001 * fs / 2
    time = np.arange(N) / fs
    b, a = signal.butter(2, 0.25, 'low')
    x = rng.normal(scale=np.sqrt(noise_power), size=time.shape)
    y = signal.lfilter(b, a, x)
    x += amp*np.sin(2*np.pi*freq*time)
    y += rng.normal(scale=0.1*np.sqrt(noise_power), size=time.shape)

    print(len(x))

    
    f, Cxy = signal.coherence(x, y, fs, nperseg=1024)
    plt.semilogy(f, Cxy)
    plt.xlabel('frequency [Hz]')
    plt.ylabel('Coherence')
    plt.show()
    """