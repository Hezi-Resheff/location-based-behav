
import pandas as pd 
import numpy as np 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap

from util import *

class trajectory_processor(pd.DataFrame):

    def __init__(self, data = None, index = None, columns = None, dtype = None, copy = False):
        return super(trajectory_processor, self).__init__(data, index, columns, dtype, copy)

    def compute_steps(self):
        return self
    
    def compute_first_passage(self, radius, max_time=np.inf):
        return self
    
    def cluster(self, target=None):
        return self
    
               
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
    
    return pd.DataFrame(data, index=f.stamp[:-1])


def trajectory_cluster(frame, target, k=3):
    """Naive clustering of trajectory, based on the values of a single column.
    :param frame: the data
    :param target: teh name of the column to use for clustering
    :param k: the number of clusters
    """    
    clusters = KMeans(n_clusters=k).fit_predict(np.atleast_2d(frame[target].values).T)
    frame["cluster"] = clusters    
    return frame

def trajectory_cluster_1(frame, target):    
    frame["cluster"] =  (frame[target].values >= .2).astype(int) + (frame[target].values >= 10).astype(int)
    return frame 
       

class MyBasemap(Basemap):     
    def printcountries(self, d=3, max_len=12):
        data = pd.io.parsers.read_csv("http://opengeocode.org/cude/download.php?file=/home/fashions/public_html/opengeocode.org/download/cow.txt", 
                                      sep=";", skiprows=28 )
        data = data[(data.latitude > self.llcrnrlat+d) & (data.latitude < self.urcrnrlat-d) & (data.longitude > self.llcrnrlon+d) & (data.longitude < self.urcrnrlon-d)]
        for ix, country in data.iterrows():                            
                plt.text(*self(country.longitude, country.latitude), s=country.BGN_name[:max_len]) 