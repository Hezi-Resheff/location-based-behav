""" The map trajectory demo """ 

import pandas as pd 
import matplotlib.pyplot as plt 
from location import *


path = "C:\\data\\Locatoin\\Storks_Africa__10_to_12_2012.csv"

# Load
animal_data = pd.DataFrame.from_csv(path, header=None, parse_dates=[2])
animal_data.columns = ["bird_id", "date", "time", "gps_lat", "gps_long"]
animal_data = animal_data.loc[animal_data.bird_id == 2334]

animal_data = trajectory_processor(animal_data, stamp=True).compute_first_passage(1)
#animal_data.find_best_fpt()



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


#(compute_steps(animal_data)["speed"].copy()+1).apply(np.log10).hist(bins=25)
#plt.show()

plt.figure()

"""
map = MyBasemap(**params)

map.drawcoastlines()
map.fillcontinents(color = 'coral')
map.drawmapboundary()          
map.drawcountries()
map.printcountries()
"""

# cluster
#clst = trajectory_cluster_1(compute_steps(animal_data), "speed")["cluster"].values 
clst = trajectory_cluster(animal_data, "FPT_1")["cluster"].values 
colors = list("grbg")

# plot
x, y = animal_data.gps_long.values, animal_data.gps_lat.values
map = plt 
map.plot(x,y, "ok", markersize=5)
for i in range(len(x)-2):
    if not np.isnan(clst[i]):
        map.plot([x[i], x[i+1]], [y[i], y[i+1]], color=colors[clst[i]])

plt.show()


