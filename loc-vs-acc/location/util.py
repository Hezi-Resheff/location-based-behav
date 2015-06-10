import pandas as pd 
import numpy as np
import os
import settings as st
from math import cos, sqrt, radians

def load_gps_csv(file_name, min_len=10):
    data = pd.DataFrame.from_csv(os.path.join(st.DATA_ROOT, file_name), parse_dates=['date_start_fix'])
    # clean bad GPS
    data = data[data.gps_status == 'A']
    # clean bad ids
    animals = data.groupby(data.bird_id).apply(len)
    good_aninmals = animals[animals > min_len].index.values
    data  = data.loc[data['bird_id'].isin(good_aninmals)]   
    return data 

def equirectangular_approx_distance(lat1, lon1, lat2, lon2):
    """
    http://www.movable-type.co.uk/scripts/latlong.html
    approx distance between GPS coordinates (not bad for small distances)
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    R = 6371 # radius of the earth in km
    x = (lon2 - lon1) * cos( 0.5*(lat2+lat1) )
    y = lat2 - lat1
    d = R * sqrt( x*x + y*y )
    return d

if __name__ == "__main__":
    #data = load_gps_csv("storks_gps_Jan2012.csv")
    #print(data)
    d = equirectangular_approx_distance(40.712784, -74.005941,  40.628546, -73.927689)
    print(d)
