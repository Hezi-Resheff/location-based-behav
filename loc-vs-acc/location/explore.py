import pandas as pd 
pd.options.display.mpl_style = 'default'
 
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap

import settings as st 
from util import *
from location import *



def cum_dist(file_name, out_img):       
    plt.figure()
    plt.hold(True)
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)                
        data['dist'].cumsum().plot()    
    plt.xlabel("Date")
    plt.ylabel("Cumulative distance")
    plt.savefig(os.path.join(st.OUT_FIG_ROOT, out_img + ".png"))
    
def trajectories(file_name, out_folder):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long"], stamp=False):
        print(animal_id)
        animal_data.plot(x="gps_long", y="gps_lat", style="-x")
        plt.savefig(os.path.join(st.OUT_FIG_ROOT, out_folder, "{}-trajectory-len-{}".format(animal_id, len(animal_data))))

def traj_map(file_name):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long"], stamp=False):  
        params = {
                'projection':'merc', 
                'lat_0':animal_data.gps_lat.mean(), 
                'lon_0':animal_data.gps_long.mean(), 
                'resolution':'h', 
                'area_thresh':0.1, 
                'llcrnrlon':animal_data.gps_long.min()-10, 
                'llcrnrlat':animal_data.gps_lat.min()-10, 
                'urcrnrlon':animal_data.gps_long.max()+10, 
                'urcrnrlat':animal_data.gps_lat.max()+10
            }
        map = Basemap(**params)
        map.drawcoastlines()
        map.drawcountries()
        map.fillcontinents(color = 'coral')
        map.drawmapboundary()          
        x, y = map(animal_data.gps_long.values, animal_data.gps_lat.values)
        map.plot(x, y, 'b-', linewidth=3)    
        plt.show()
                              
def traj_clustres(file_name):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"], stamp=True):
        data = compute_steps(animal_data)
        data = trajectory_cluster(data, "speed", k=3)                
        data["long"] = animal_data.gps_long[1:].values
        data["lat"] = animal_data.gps_lat[1:].values
        
        #ax = data.plot(x='long', y='lat', style="-", color='black')
        plt.hold(True)
        for i in range(len(data)-1):                        
            c = list("rgbmyk")[data.iloc[i+1].cluster] 
            plt.plot([data.iloc[i].long, data.iloc[i+1].long], [data.iloc[i].lat, data.iloc[i+1].lat], color=c, linestyle='-', linewidth=1)
                   
        plt.savefig(os.path.join(st.OUT_FIG_ROOT, out_folder, "{}-trajectory-len-{}".format(animal_id, len(animal_data))))
        plt.close()
        
                                    
def speed_n_dist_hist(file_name, out_folder):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)
        data.hist(column=["dist", "speed"], bins=20)                
        plt.savefig(os.path.join(st.OUT_FIG_ROOT, out_folder, "{}-dist-speed-all".format(animal_id)))
        data.loc[data.dist > 1].hist(column=["dist", "speed"], bins=40)                
        plt.savefig(os.path.join(st.OUT_FIG_ROOT, out_folder, "{}-dist-speed-where-dist-largerthan-1".format(animal_id)))

def time_delta(file_name):
    lags = []
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)
        lag = data.apply(lambda row: row.time.total_seconds(), axis=1) / 60
        lags.extend(lag.values.tolist())
    l = pd.Series(lags)
    l.hist()
    plt.show()
    plt.figure()
    l[l>22].hist(bins=100)    
    plt.show()


if __name__ == "__main__":
    #cum_dist("storks_gps_Jan2012.csv")
    #trajectories("storks_gps_Jan2012.csv")
    #speed_n_dist_hist("storks_gps_Jan2012.csv")
    #traj_clustres("storks_gps_Jan2012.csv")
    traj_map("storks_gps_Jan2012.csv")
    #cum_dist("storks_gps_Jan2012.csv", out_img="cumlulative_all_Jan2012")
    #trajectories("storks_gps_Jan2012.csv", out_folder="trajectories")
    #speed_n_dist_hist("storks_gps_Jan2012.csv", out_folder="histograms-speed-dist")
    #traj_clustres("storks_gps_Jan2012.csv","trajectories-cluster-speed")
    #time_delta("storks_gps_Jan2012.csv")