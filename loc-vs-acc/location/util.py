import pandas as pd 
import numpy as np
import os
import settings as st

def load_gps_csv(file_name, min_len=10):
    data = pd.DataFrame.from_csv(os.path.join(st.DATA_ROOT, file_name), parse_dates=['date_start_fix'])
    # clean bad GPS
    data = data[data.gps_status == 'A']
    # clean bad ids
    animals = data.groupby(data.bird_id).apply(len)
    good_aninmals = animals[animals > min_len].index.values
    data  = data.loc[data['bird_id'].isin(good_aninmals)]   
    return data 

if __name__ == "__main__":
    data = load_gps_csv("storks_gps_Jan2012.csv")
    print(data)

