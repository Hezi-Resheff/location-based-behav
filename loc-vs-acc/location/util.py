import pandas as pd 
import numpy as np
import os
import settings as st

def load_gps_csv(file_name):
    data = pd.DataFrame.from_csv(os.path.join(st.DATA_ROOT, file_name), parse_dates=['date_start_fix'])
    # clean
    data = data[data.gps_status == 'A']
    return data 

if __name__ == "__main__":
    data = load_gps_csv("storks_gps_Jan2012.csv")
    print(data)

