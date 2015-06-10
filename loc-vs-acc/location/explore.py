import pandas as pd 
import numpy as np 

import settings as st 
from util import *

def compute_steps(frame):
    """ Compute the distance time and speed between points.
    :param frame: Each row is a point. 
    """
    f = frame
    f1 = f.shift(1)
        
    data = [
        { "time": f.loc[ix, "stamp"] - f1.loc[ix, "stamp"],
           "dist": equirectangular_approx_distance(f.loc[ix, "gps_lat"], f.loc[ix, "gps_long"], f1.loc[ix, "gps_lat"], f1.loc[ix, "gps_long"])
        }
        for ix in f.index[1:]]
    for p in data:    
        p["speed"] = p["dist"] / (p["time"].total_seconds() / pd.Timedelta("1h").total_seconds())
    
    return pd.DataFrame(data, index=f.index[1:])


def step_dist(file_name):
    data = load_gps_csv(file_name)
    for animal_id, animal_data in data.groupby(data.bird_id):        
        
        animal_data['stamp'] = animal_data.apply(lambda row: row.date_start_fix + pd.Timedelta(row.time_start_fix), axis=1)        
        data = compute_steps(animal_data[["gps_lat", "gps_long", "stamp"]])
       
      
        print(data)
            
        
        


if __name__ == "__main__":
    step_dist("storks_gps_Jan2012.csv")