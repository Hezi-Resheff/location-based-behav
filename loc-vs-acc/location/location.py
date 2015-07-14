
import pandas as pd 
import numpy as np 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap
#Basemap = object 

from util import *

class trajectory_processor(pd.DataFrame):

    def __init__(self, data = None, index = None, columns = None, dtype = None, copy = False, stamp=True):
        super(trajectory_processor, self).__init__(data, index, columns, dtype, copy)
        
        if "stamp" in self.columns:
            self.sort("stamp", inplace=True)
        
        elif stamp:
            self['stamp'] = self.apply(lambda row: row.date + pd.Timedelta(row.time), axis=1)    
            self.drop(["date","time"], axis=1, inplace=True)
                
        self.reset_index(drop=True, inplace=True)

    def compute_steps(self):
        """ compute time/dist/speed per sample; last row gets just 1 for all params and should be deleted later using clean_day_end """
        self["time"] = [self.ix[ix+1, "stamp"] - self.ix[ix, "stamp"] for ix in range(len(self)-1)] + [pd.Timedelta("1h")]
        self["dist"] = [equirectangular_approx_distance(self.ix[ix, "gps_lat"], self.ix[ix, "gps_long"], self.ix[ix+1, "gps_lat"], self.ix[ix+1, "gps_long"]) for ix in range(len(self)-1)] + [1]
        self["speed"] =  self.apply(lambda p: p["dist"] / (p["time"].total_seconds() / pd.Timedelta("1h").total_seconds()), axis=1) 
        #self.ix[len(self)-1, ["time", "dist", "speed"]] = np.NaN        
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
                self.ix[i, col_name] = pd.Timedelta("{}h".format(hard_max))
                              
        self[col_name] = self[col_name].astype('timedelta64[s]') / 3600 
        self[col_name] = self[col_name].apply(lambda val: min(val, hard_max))
        return self

    def cluster(self, target, k=3):
        data = self[target].values
        data = data[np.logical_not(np.isnan(data))]
        km = KMeans(n_clusters=k).fit(np.atleast_2d(data).T)
        
        # We want the cluster index to be sorted by the values of the centroids (in order to compare runs)
        km.cluster_centers_.ravel().sort()

        self["cluster"] = [km.predict([val])[0] if not np.isnan(val) else val for val in self[target].values]    
        return self


    def find_best_fpt(self, radii=None, plot=True, hard_max=3):
        """ Use max variance criterion for best radius of FPT """
        if radii is None:
            radii = [.1, .5, 1, 2, 5, 10, 25]

        # compute 
        for rad in radii:
            print(rad)
            self.compute_first_passage(rad, hard_max=hard_max)

        # Need to remove the last point of each day, otherwie (since there are no recordings at night) we get that the FPT is
        # the time until the next recording of the next day, and the var is inflated. 
        self.clean_day_end() 

        # diagnostics 
        vars = [self["FPT_" + str(rad)].std() for rad in radii]           
        self._fpt_diag = zip(radii, vars)
        
        if plot:
            plt.plot(radii, vars, "x-", markersize=10)
            plt.xlabel("radius [Km]", fontsize=24)
            plt.ylabel("std(FPT) [h]", fontsize=24)
            plt.show()

        return self 

    def diluted(self, rad=1.0):
        """ Return a diluted version of this trajectory --- good for plotting """
        out = []         
        last_lat, last_lon = 0, 0 # data is all far form this... 
        for i in range(len(self)):
            if equirectangular_approx_distance(self.ix[i ,"gps_lat"], self.ix[i, "gps_long"], last_lat, last_lon) > rad:
                last_lat, last_lon = self.ix[i ,"gps_lat"], self.ix[i, "gps_long"]
                out.append((last_lon, last_lat))
        return np.array(out)

    def clean_day_end(self):
        """ Remove the last point of each day
            This is useful for cases where the dist/speed/etc. is computed based on the *next* point
            which in this case doesn't exist (and is carried over to the next day).
        """
        days = [s.date() for s in self["stamp"]]
        ix = self["stamp"].groupby(days).apply(np.argmax).values
        self.drop(ix, axis=0, inplace=True)
        self.reset_index(drop=True, inplace=True)                
        return self 
    
    @classmethod
    def stamp(Cls, file_path_in, columns, date_cols, file_path_out):
        """ Convert date/time to stamp """
        raw_data = pd.DataFrame.from_csv(file_path_in, header=None, parse_dates=date_cols)
        raw_data.columns = columns
        Cls(raw_data, stamp=True).to_csv(file_path_out)
        
     

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

                
if __name__ == "__main__":
    from settings import DATA_ROOT
    in_file = os.path.join(DATA_ROOT, "Storks_Africa__10_to_12_2012__with_behav__ALL.csv")
    cols = ["bird_id", "date", "time", "gps_lat", "gps_long", "behav", "ODBA"]
    
    #trajectory_processor.stamp(in_file, cols, [2], in_file)    
    #print("Done!")

    data  = pd.DataFrame.from_csv(in_file, parse_dates=["stamp"])
    animal = data["bird_id"].unique()
    data = data[data.bird_id == animal[0]]
    print(data.head())

    data = trajectory_processor(data, stamp=False).compute_steps().clean_day_end()

    print(data.head(10))
    print("Done!")