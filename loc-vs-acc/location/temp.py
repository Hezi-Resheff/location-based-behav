""" Just for fun """

import pandas as pd 
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap

class MyBasemap(Basemap):     
    def printcountries(self, d=3, max_len=12):
        data = pd.io.parsers.read_csv("http://opengeocode.org/cude/download.php?file=/home/fashions/public_html/opengeocode.org/download/cow.txt", 
                                      sep=";", skiprows=28 )
        data = data[(data.latitude > self.llcrnrlat+d) & (data.latitude < self.urcrnrlat-d) & (data.longitude > self.llcrnrlon+d) & (data.longitude < self.urcrnrlon-d)]
        for ix, country in data.iterrows():                            
                plt.text(*self(country.longitude, country.latitude), s=country.BGN_name[:max_len]) 


path = "C:\\Users\\t-yeresh\\data\\storks2012\\storks_2012_GPS_sparse.csv"

animal_data = pd.DataFrame.from_csv(path, header=None)
animal_data.columns = ["date", "time", "gps_lat", "gps_long"]
animal_data = animal_data.loc[animal_data.index == 17870582]
animal_data = animal_data[animal_data.gps_lat != 0]

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

x, y = map(animal_data.gps_long.values, animal_data.gps_lat.values)

map.plot(x, y, 'b-', linewidth=1)    
plt.show()


