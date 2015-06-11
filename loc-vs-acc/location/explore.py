import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

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
    time_delta("storks_gps_Jan2012.csv")