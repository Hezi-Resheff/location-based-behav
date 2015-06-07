import pandas as pd 
import numpy as np 

import settings as st 
from util import *

def step_dist(file_name):
    data = load_gps_csv(file_name)
    for animal_id, animal_data in data.groupby(data.bird_id):        
        print(animal_id)        
        print(animal_data[['date_start_fix', 'time_start_fix']])
    




if __name__ == "__main__":
    step_dist("storks_gps_Jan2012.csv")