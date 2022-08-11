from tracemalloc import start
import numpy as np
from datetime import datetime,timedelta,timezone,tzinfo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def extract(rain_df,start_date_utc,end_date_utc):
    """
    extrait du dataframe toutes les lignes dont la date est comprise dans la période de temps
    Si les dates sont entre deux mesures, renvoie un tableau contenant les valeurs de la mesure la plus proche

    Args :
        rain_df (pandas dataframe) : dataframe dont on veut extraire les lignes
        start_date_utc (datetime) : date marquant le début de la période d'extraction
        end_date_utc (datetime) : date marquant la fin de la période d'extraction
    """
    rain_df['time'] = pd.to_datetime(rain_df['time'],utc=True)
    mask = (rain_df['time'] > start_date_utc) & (rain_df['time'] <= end_date_utc)
    out_df = rain_df.loc[mask]
    
    if out_df.empty and (rain_df['time'].array[0] < start_date_utc < rain_df['time'].array[-1]) :
        nearest_gap = np.argmin(np.abs(rain_df['time']-start_date_utc))
        out_df = rain_df.loc[nearest_gap]
    
    return out_df

def plot(rain,mtd_fn,cols=False,title=False):
    """
    Affiche les valeurs de pluie

    Args:
        rain (str, pandas dataframe) : pandas dataframe ou lien vers le csv contenant les données pluies à afficher
        mtd_fn (str) : fichier csv contenant les métadonnées
        cols (bool, list) : liste des indices des colonnes à afficher (Default False)
        title (bool, str) : titre du graphique (Default False)
    """
    if isinstance(rain, str):
        rain_df = pd.read_csv(rain)
    else:
        rain_df = rain
    mtd = pd.read_csv(mtd_fn)

    if rain_df.index.name != 'time':
        rain_df['time'] = pd.to_datetime(rain_df['time'],utc=True)
        rain_df.set_index("time",inplace=True)

    dates = rain_df.index.values
    
    if cols == False:
        cols = rain_df.columns[1:]
    elif type(cols[0]) == int:
        cols = [rain_df.columns[col_idx] for col_idx in cols]
    
    names = [mtd.loc[mtd["Numéro"]==int(col)]["Nom"].array[0].replace("\xa0"," ") for col in cols]
    
    fig, ax = plt.subplots(ncols=1)
    
    if title:
        fig.suptitle(title)
    
    for col in cols:
        ax.plot_date(dates, rain_df[col], markersize=3, linestyle='solid')

    locator = mdates.AutoDateLocator()
    
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.legend(names)
    fig.autofmt_xdate()
    ax.set_ylabel('moyenne des pluies sur la période (mm/h)')
    ax.set_xlabel('mois')
    
    plt.show()
    

if __name__ == '__main__':

    fn_src = r"../data/pluie_sol/gauges_guyane_6min_utc.csv"
    fn_1h = r"../data/pluie_sol/gauges_guyane_1h_utc.csv"
    fn_1m = r"../data/pluie_sol/gauges_guyane_1m_utc.csv"
    fn_mtd = r"../data/pluie_sol/gauges_guyane_metadata.csv"

    plot(fn_1h,fn_mtd,[6])
    """
    # ouverture du fichier source, somme horaire et enregistrement
    rain_df = pd.read_csv(fn_src)
    rain_df['time'] = pd.to_datetime(rain_df['time'],utc=True) 
    rain_df.set_index("time",inplace=True)
    rain_df_agreg_1h = rain_df.resample(timedelta(hours=1)).agg(pd.Series.sum, skipna=False)
    rain_df_agreg_1h.to_csv(fn_1h)
    """

    """
    # ouverture fichier avec précipitations en mm/h
    # moyennage sur le mois et enregistrement du fichier
    rain_df = pd.read_csv(fn_1h)
    rain_df['time'] = pd.to_datetime(rain_df['time'],utc=True)
    rain_df.set_index("time",inplace=True)
    rain_df_agreg_1m = rain_df.resample("M").mean()
    rain_df_agreg_1m.to_csv(fn_1m)
    plot(rain_df_agreg_1m,fn_mtd,[6])
    """
    
    """
    # extraction des précipitations en mm/h
    start_date  = datetime(2020,1,1,tzinfo=timezone.utc)
    end_date    = datetime(2020,12,31,tzinfo=timezone.utc)
    rain_df = pd.read_csv(fn_1h)
    rain_df_extr = extract(rain_df,start_date,end_date)
    plot(rain_df_extr,fn_mtd,[0,1,2])
    """
    
