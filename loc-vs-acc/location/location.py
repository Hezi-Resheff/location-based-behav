
import pandas as pd 
import numpy as np 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt 
#from mpl_toolkits.basemap import Basemap
Basemap = object 

from util import *

class trajectory_processor(pd.DataFrame):

    def __init__(self, data = None, index = None, columns = None, dtype = None, copy = False, stamp=True):
        super(trajectory_processor, self).__init__(data, index, columns, dtype, copy)
        if stamp:
            self['stamp'] = self.apply(lambda row: row.date + pd.Timedelta(row.time), axis=1)    
            self.drop(["date","time"], axis=1, inplace=True)
        self.sort("stamp", inplace=True)
        self.reset_index(drop=True, inplace=True)

    def compute_steps(self):
        return self
    
    def compute_first_passage(self, radius, col_name=None, hard_max=3):
        """ For each data point, compute the time delta until it first crosses the boundry of the *radius* circle around it """
        if col_name is None:
            col_name = "FPT_" + str(radius)
        self[col_name] = 0
        
        # TODO: find a better way of computing FPT! Can use geometric stuff to reduce time... 
        N = len(self)
        for i in range(N):  
            j = i + 1
            while j < N - 1:                                               
                d = equirectangular_approx_distance(self.ix[i ,"gps_lat"], self.ix[i, "gps_long"], self.ix[j, "gps_lat"], self.ix[j, "gps_long"])
                if d >= radius:                    
                    self.ix[i, col_name] = self.ix[j, "stamp"] - self.ix[i, "stamp"]
                    break
                j += 1 
            else:                
                # end of data
                self.ix[i, col_name] = np.NaN                   
        self[col_name] = self[col_name].astype('timedelta64[s]') / 3600 
        self[col_name] = self[col_name].apply(lambda val: min(val, hard_max))
        return self

    def cluster(self, target=None, k=3):
        data = self[target].values
        data = data[np.logical_not(np.isnan(data))]
        km = KMeans(n_clusters=k).fit(np.atleast_2d(data).T)
        self["cluster"] = [km.predict([val])[0] if not np.isnan(val) else val for val in self[target].values]    
        return self


    def find_best_fpt(self, radii=None, plot=True):
        """ Use max variance criterion for best radius of FPT """
        if radii is None:
            radii = [.1, .5, 1, 2, 5, 10, 25]

        # compute 
        for rad in radii:
            self.compute_first_passage(rad)

        # diagnostics 
        vars = [self["FPT_" + str(rad)].std() for rad in radii]           
        self._fpt_diag = zip(radii, vars)
        
        if plot:
            plt.plot(radii, vars, "x-", markersize=10)
            plt.xlabel("radius [Km]", fontsize=24)
            plt.ylabel("std(FPT) [h]", fontsize=24)
            plt.show()

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

