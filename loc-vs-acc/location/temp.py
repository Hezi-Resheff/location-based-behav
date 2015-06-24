""" Just for fun """

import pandas as pd 
import matplotlib.pyplot as plt 
from location import *


path = "C:\\Users\\t-yeresh\\data\\acc_location\\StorksIL2013.csv"

# Load
animal_data = pd.DataFrame.from_csv(path, header=None, parse_dates=[2])
animal_data.columns = ["bird_id", "date", "time", "gps_lat", "gps_long"]

# select animal and claen
animal_data = animal_data.loc[animal_data.bird_id == 3180]
#animal_data = animal_data[animal_data.gps_lat != 0]
#animal_data.reset_index(inplace=True) 

#sort  by timestamp
animal_data['stamp'] = animal_data.apply(lambda row: row.date + pd.Timedelta(row.time), axis=1)    
animal_data.sort("stamp", inplace=True)

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

plt.figure()
map = MyBasemap(**params)

map.drawcoastlines()
map.fillcontinents(color = 'coral')
map.drawmapboundary()          
map.drawcountries()
map.printcountries()

# cluster
clst = trajectory_cluster(compute_steps(animal_data), "speed")["cluster"].values 
cols = np.array(list("brgb"))[clst]

# plot
x, y = map(animal_data.gps_long.values, animal_data.gps_lat.values)
map.plot(x,y, "xk")
for i in range(len(x)-2):
    map.plot([x[i], x[i+1]], [y[i], y[i+1]], color=cols[i])

plt.show()


