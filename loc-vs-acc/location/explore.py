import pandas as pd 
import numpy as np 

import settings as st 
from util import *

def step_dist(file_name):
    data = load_gps_csv(file_name)
    print(data.groupby(data.bird_id).count().icol(0))
        
    




if __name__ == "__main__":
    step_dist("storks_gps_Jan2012.csv")