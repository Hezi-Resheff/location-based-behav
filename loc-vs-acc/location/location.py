

import pandas as pd 
import numpy as np 
from sklearn.cluster import KMeans

from util import *

def compute_steps(frame):
    """ Compute the distance time and speed between points.
    :param frame: Each row is a point. 
    """
    f = frame
    f1 = f.shift(1)
        
    data = [
        {           
           "time": f.loc[ix, "stamp"] - f1.loc[ix, "stamp"],
           "dist": equirectangular_approx_distance(f.loc[ix, "gps_lat"], f.loc[ix, "gps_long"], f1.loc[ix, "gps_lat"], f1.loc[ix, "gps_long"])
        }
        for ix in f.index[1:]]
    for p in data:    
        p["speed"] = p["dist"] / (p["time"].total_seconds() / pd.Timedelta("1h").total_seconds())
    
    return pd.DataFrame(data, index=f.stamp[1:])

def trajectory_cluster(frame, target, k=3):
    """Naive clustering of trajectory, based on the values of a single column.
    :param frame: the data
    :param target: teh name of the column to use for clustering
    :param k: the number of clusters
    """    
    clusters = KMeans(n_clusters=k).fit_predict(np.atleast_2d(frame[target].values).T)
    frame["cluster"] = clusters
    return frame
    
    
