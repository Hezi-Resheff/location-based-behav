import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap

import settings as st 
from util import *
from location import *



def cum_dist(file_name):       
    plt.figure()
    plt.hold(True)
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)                
        data['dist'].cumsum().plot()    
    plt.xlabel("Date")
    plt.ylabel("Cumulative distance")
    plt.show()
    
def trajectories(file_name):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long"], stamp=False):
        print(animal_id)
        animal_data.plot(x="gps_long", y="gps_lat", style="-x")
        plt.show()

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
            c = list("rgb")[data.iloc[i+1].cluster] 
            plt.plot([data.iloc[i].long, data.iloc[i+1].long], [data.iloc[i].lat, data.iloc[i+1].lat], color=c, linestyle='-', linewidth=1)
                   
        plt.show()
                                            
def speed_n_dist_hist(file_name):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)
        data.hist(column=["dist", "speed"], bins=20)                
        data.loc[data.dist > 1].hist(column=["dist", "speed"], bins=40)                
        plt.show()

def time_delta(file_name):
    for animal_id, animal_data in iter_animal(file_name, cols=["gps_lat", "gps_long", "stamp"]):
        data = compute_steps(animal_data)
        lag = data.apply(lambda row: row.time.total_seconds(), axis=1) / 60
        lag.hist(bins=100)
        plt.figure()
        lag[lag>21].hist(bins=100)
        plt.show()


if __name__ == "__main__":
    #cum_dist("storks_gps_Jan2012.csv")
    #trajectories("storks_gps_Jan2012.csv")
    #speed_n_dist_hist("storks_gps_Jan2012.csv")
    #traj_clustres("storks_gps_Jan2012.csv")
    traj_map("storks_gps_Jan2012.csv")