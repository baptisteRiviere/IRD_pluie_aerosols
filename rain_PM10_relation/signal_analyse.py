import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys
from datetime import datetime, timezone
from scipy.stats import pearsonr,spearmanr
sys.path.insert(0, r'pluie')
import skccm as ccm
from skccm.utilities import train_test_split



def join_rain_PM10(rain_path,PM10_dir,out_dir,place="cay",data_rain="pluvio",start_year=2010,end_year=2020):
    """
    Effectue la jointure entre les données de pluie et les données PM10 jour par jour

    Args:
        rain_path (string) : chemin d'accès aux donnée pluie
        PM10_dir (string) : chemin d'accès au dossier contenant les données PM10
        out_dir (string) : chemin d'accès au dossier où seront enrgistrés les résultats
        place (string) : accronyme de la ville étudiée
        data_rain (string) : source de la donnée pluie
    
    Returns:
        result_df (pandas dataframe) : dataframe contenant les deux séries associées
    """
    
    # lecture du fichier pluie et rééchantillonnage
    rain_df = pd.read_csv(rain_path)                                    
    rain_df['date'] = pd.to_datetime(rain_df['time'])                   # conversion de la colonne time en date 
    rain_df = rain_df.resample('D',on='date').sum()                     # agregation des données à la journée
    
    # initialisation dataframe final et index des codes communes
    result_df = pd.DataFrame()
    places_idx = {"cay":"97307001","geo":"97308001","lau":"97311001","kou":"97304005","mat":"97307001"}
    
    # on parcourt chaque année dont on possède des données PM10
    for year in [y for y in range(start_year,end_year+1)]:
        PM10_path = PM10_dir + rf"/Donnees_PM10_{year}.xlsx"            # nom du fichier PM10
        PM10_df = pd.read_excel(PM10_path,skiprows=[1,2])               # lecture du fichier
        PM10_df['date'] = pd.to_datetime(PM10_df['Date'])               # conversion de la date
        PM10_df = PM10_df.resample('D', on='date').mean()               # rééchantillonage : moyenne quotidienne
        place_colname = PM10_df.columns[np.argmax([place in col.lower() for col in PM10_df.columns])]
                                                                        # recherche du nom de colonne renvoyant à la ville concernée
        # fusion des deux tableaux sur l'année et harmonisation
        part_result_df = pd.concat([PM10_df[[place_colname]], rain_df[places_idx[place]]], axis=1, join="inner")
        part_result_df = part_result_df.rename(columns={place_colname: "PM10", places_idx[place]: "rain"})
        
        # ajout au tableau final
        result_df = pd.concat([result_df,part_result_df]) 
        
    # sauvegarde du fichier
    out_path = out_dir + rf"/PM10_pluie_{data_rain}_{start_year}-{end_year}_{place}.csv"
    result_df.to_csv(out_path)
    return result_df
    
def path2arrays(in_path,start_date=None,end_date=None,fillna=True):
    """
    Conversion d'un fichier en sortie de join_rain_PM10 en arrays séparés
    
    Args:
        in_path (string) : chemin d'accès au fichier dont on veut extraire les arrays
        start_date (datetime) : borne inférieure de la période d'intéret
        end_date (datetime) : borne supérieure de la période d'intéret
        fillna (Bool) : si vrai, ajoute la valeur 0 si il manque une valeur pour conserver la périodicité
    """
    # lecture du fichier csv
    df = pd.read_csv(in_path)

    # conversion de l'index
    df['date'] = pd.to_datetime(df['date'],utc=True)

    # extraction des dates d'intérêt
    if start_date != None:
        df = df.loc[(df['date'] >= start_date)]
    if end_date != None:
        df = df.loc[(df['date'] <= end_date)]

    # pour conserver la périodicité : remplacement NaN par valeurs nulles
    if fillna:
        nb_nan = df.isna().sum().sum()
        print(f"nombre de dates sans valeur : {nb_nan}")
        df = df.fillna(0)  

    # extraction des array
    PM10_array = df["PM10"].array ; rain_array = df["rain"].array ; dates = df["date"]
    return PM10_array,rain_array,dates

def coherence(list1,list2,list1name="list 1",list2name="list 2",plot=True):
    """
    applique la fonction de cohérence aux deux séries de données en entrée
    Toute valeur manquante sera remplacée par une valeur nulle pour conserver la continuité

    Args: 
        list1 (numpy array) : première liste étudiée 
        list2 (numpy array) : seconde liste étudiée
        list1name (string) : nom de la première liste (par défaut "list 1")
        list2name (string) : nom de la seconde liste (par défaut "list 2")
        
    Returns:
        f_ (numpy array) : fréquence des mesures en Hz
        Cxy (numpy array) : fonction de cohérence
    """

    # définition des paramètres
    freq = 1                        # fréquence d'échantionnage à 1 jour
    nbelem = len(list1)        # nombre d'éléments
    nperseg = 366                   # nombre de dates par fenêtre de Hann

    # calcul de la cohérence
    f, Cxy = signal.coherence(list1,list2,fs=freq,nperseg=nperseg)
    f_ = f/(60*60*24)               # conversion de la fréquence en Hz

    # affichage des paramètres
    print(f"frequence échant= {freq}")
    print(f"nperseg = {nperseg}")
    print(f"nombre d'éléments = {nbelem}")
    print(f"nombre de points = {len(Cxy)}")
    print(f"cohérence max = {np.max(Cxy)}")

    # affichage de la courbe des résultats
    if plot:
        plt.plot(f_, Cxy)
        plt.grid()
        plt.title(f"fonction de cohérence entre {list1name} et {list2name}")
        plt.xlabel('fréquence [Hz]')
        plt.ylabel('cohérence')
        plt.show()

    return f_,Cxy

def coherence_multiple_series(paths,legend=["1","2"]):
    """
    Permet de tracer et de comparer les fonctions de cohérence de plusieurs séries

    Args:
        paths (list) : liste des chemins d'accès aux fichiersà extraire
    """
    start_date, end_date = datetime(2016,1,1,tzinfo=timezone.utc),datetime(2020,12,31,tzinfo=timezone.utc)
    for path in paths:
        PM10_array,rain_array,dates = path2arrays(path)

        f_,Cxy = coherence(PM10_array,rain_array,plot=False)
        plt.plot(f_, Cxy)

    plt.grid()
    plt.xlabel('fréquence [Hz]')
    plt.ylabel('cohérence')
    plt.legend(legend)
    plt.show()

def conv_cross_map(list1,list2,list1name="list 1",list2name="list 2",lag=5,embed=3):
    """
    Algorithme de convergent cross  appliqué aux listes 1 et 2

    Args: 
        list1 (numpy array) : première liste étudiée 
        list2 (numpy array) : seconde liste étudiée
        list1name (string) : nom de la première liste (par défaut "list 1")
        list2name (string) : nom de la seconde liste (par défaut "list 2")
        lag (int) : valeur de lag pour l'intégration (par défaut 5)
        embed (int): valeur de embed pour l'intégration (par défaut 3)
    """
    
    # intégration
    e1 = ccm.Embed(list1)
    e2 = ccm.Embed(list2)
    X1 = e1.embed_vectors_1d(lag,embed)
    X2 = e2.embed_vectors_1d(lag,embed)

    # division des séries en séries de test et d'entrainement
    x1tr, x1te, x2tr, x2te = train_test_split(X1,X2, percent=.75)

    # initialisation de la classe CCM
    CCM = ccm.CCM()

    # définition des différentes tailles de librairie
    len_tr = len(x1tr)
    lib_lens = np.arange(50, len_tr, len_tr/50, dtype='int')

    # entrainement et prédiction
    CCM.fit(x1tr,x2tr)
    x1p, x2p = CCM.predict(x1te, x2te,lib_lengths=lib_lens)

    # calcul des scores
    sc1,sc2 = CCM.score()

    # affichage des résultats
    fig, ax = plt.subplots(ncols=1)
    ax.plot(lib_lens,sc1, markersize=3, linestyle='solid')
    ax.plot(lib_lens,sc2, markersize=3, linestyle='solid')
    ax.legend([f"{list1name} -> {list2name}",f"{list2name} -> {list1name}"])
    ax.set_ylabel('R²')
    ax.set_xlabel('taille de la librairie')
    plt.show()

def correlation(list1,list2,list1name="list 1",list2name="list 2"):
    """
    calcul de la corrélation de Spearman entre les deux séries en entrée

    Args: 
        list1 (numpy array) : première liste étudiée 
        list2 (numpy array) : seconde liste étudiée
        list1name (string) : nom de la première liste (par défaut "list 1")
        list2name (string) : nom de la seconde liste (par défaut "list 2")

    Returns:
        corr (float) : corrélation
    """
    
    corr, _ = spearmanr(list1, list2)

    print(f"CC SPEARMAN = {round(corr,3)}")

    plt.scatter(list1,list2,s=50,alpha=0.8)
    plt.xlabel(list1name)
    plt.ylabel(list2name)
    plt.grid()
    plt.show()

    return corr

def plot(dates,list1,list2,list1name="list 1",list2name="list 2"):
    """
    affichage des deux séries

    Args: 
        list1 (numpy array) : première liste à afficher
        list2 (numpy array) : seconde liste à afficher
        list1name (string) : nom de la première liste (par défaut "list 1")
        list2name (string) : nom de la seconde liste (par défaut "list 2")
    """
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

def plot_sum_month(df):
    """
    affichage de l'agréagation des deux séries par mois

    Args: 
        df (pandas dataset) : dataframe contenant les données à agréger
    """
    PM10_by_month = []
    rain_by_month = []
    for month in range(1,13):
        df["month"] = pd.DatetimeIndex(df['date']).month
        df_month = df.loc[(df["month"] == month)]
        PM10_by_month.append(df_month["PM10"].sum())
        rain_by_month.append(df_month["rain"].sum())
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.array(rain_by_month)/11)
    ax.plot(np.array(PM10_by_month)/11)
    ax.xaxis.set_ticks(range(12))
    ax.xaxis.set_ticklabels(["jan","fev","mar","avr","mai","jui","jui","aou","sep","oct","nov","dec"])
    plt.legend(["pluviométrie (mm par an)","PM10 (μg/m³ par an)"])
    plt.show()


if __name__ == "__main__":

    # définition des chemins d'accès aux fichiers source de pluie
    pluvio_rain_path = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"
    IMERG_rain_path = r"../data/estimation_rain/evaluation/estim_IMERG_cayenne.csv"

    # définition du dossier contenant les données PM10 par année
    PM10_dir = r"../data/PM10"

    # définition du dossier de sortie 
    out_dir = r"../data/analyse_series_temp"

    place = "cay"
    data_src = "IMERG"
    start_year, end_year = 2010,2020

    #join_rain_PM10(IMERG_rain_path,PM10_dir,out_dir,place,data_src)

    data_path = out_dir + rf"/PM10_pluie_{data_src}_{start_year}-{end_year}_{place}.csv"
    start_date,end_date = None,None
    start_date,end_date = datetime(2016,1,1,tzinfo=timezone.utc),datetime(2020,12,31,tzinfo=timezone.utc)
    PM10_array,rain_array,dates = path2arrays(data_path,start_date,end_date,fillna=True)
        
    #coherence(PM10_array,rain_array,"concentration de PM10",f"pluviométrie par {data_src}",True)

    data_path_pluvio = out_dir + rf"/PM10_pluie_pluvio_2010-2020_cay.csv"
    data_path_IMERG = out_dir + rf"/PM10_pluie_IMERG_2010-2020_cay.csv"
    #coherence_multiple_series([data_path_pluvio,data_path_IMERG],["pluviomètre","IMERG"])

    #correlation(PM10_array,rain_array,"PM10","pluie")

    #conv_cross_map(PM10_array,rain_array,"PM10","IMERG",lag=5,embed=3)
    
    #plot(dates,PM10_array,rain_array,"PM10 (μg/m³)","pluie (mm/jour)")

    #plot_sum_month(df)