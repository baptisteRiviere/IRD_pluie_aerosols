import pandas as pd
from datetime import datetime, timedelta
import sys
import json

sys.path.insert(0, r'pluie/API_IMERG')
from IMERG_download import download_IMERG_image

sys.path.insert(0, r'Images')
from File import File


def merge_PM10_tables():
    list_AOT_path = [rf"../data/pic_mean_AOT/tableau_pics_mean_AOT_{name}.xlsx" for name in ["inf_50","sup_50","sup_100","sup_150"]]
    AOT_final_df = pd.DataFrame()
    start_date, end_date = datetime(2013,1,1), datetime(2020,12,31)
    day_count = (end_date-start_date).days + 1
    iter_count=0
    for d in (start_date + timedelta(n) for n in range(day_count)):
        iter_count+=1
        for AOT_df in [pd.read_excel(AOT_path) for AOT_path in list_AOT_path]:
            AOT_d = AOT_df.loc[AOT_df['Date'] == datetime.strftime(d,"%Y-%m-%d")]
            AOT_array = AOT_d["Cayenne"].array
            if len(AOT_array):
                AOT_final_df = pd.concat([AOT_final_df,AOT_d],ignore_index=True)
                if iter_count%10 == 0:
                    print(f"{iter_count}/{day_count}")
            
    AOT_final_df.drop("Unnamed: 0", inplace=True, axis=1)
    AOT_final_df.set_index("Date")
    AOT_final_df.to_excel(r"../data/pic_mean_AOT/tableau_pics_mean_AOT.xlsx")


if __name__ == "__main__":
    projection = json.load(open(r"../data/param_proj/param_guy.json", "r", encoding="utf-8"))
    csv_path = r"../data/analyses_pluie/analyse_pluies_campagne_1.csv"
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'],utc=True)
    dates = df['date'].array
    for d in dates:
        print(d)
        result = download_IMERG_image(d,dir,mode="Late")
        if result != False:
            (fn,std,end) = result
            file = File(fn)
            #a = file.getPxlValue(self,lat,lon,attribute="HQprecipitation")
            img = file.project(projection,"HQprecipitation")
            img.show()
            #print(a)

        break


# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974],nv
# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220404-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974],nv

# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],randomError[0:0][1242:1300][915:974],time_bnds[0:0][0:1],time,lon[1242:1300],lat[915:974]
a = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],time,lon[1242:1300],lat[915:974]"
b = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.06/2022/04/3B-DAY-L.MS.MRG.3IMERG.20220402-S000000-E235959.V06.nc4.nc4?HQprecipitation[0:0][1242:1300][915:974],time,lon[1242:1300],lat[915:974]"

print(a==b)