import pandas as pd
from datetime import datetime, timedelta


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
