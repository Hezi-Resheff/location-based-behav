import pandas as pd 
import numpy as np
import os 

from location import trajectory_processor
from settings import DATA_ROOT

def compare_behav_types(data_file, min_sampels=2000, r=1, hard_max=3):

    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, header=None, parse_dates=[2])
    animal_data.columns = ["bird_id", "date", "time", "gps_lat", "gps_long", "behav", "ODBA"]
    animal_data.behav = animal_data.behav.replace("\\N", -1).apply(int) # Clean animal behav and add the unknown==-1 style 

    animals = animal_data["bird_id"].unique()
    out = {}
    outn = {} # normalized
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:            
            continue 
        
        data = trajectory_processor(data, stamp=True).compute_first_passage(r, hard_max=hard_max).cluster("FPT_{}".format(r), k=3)
        pivot = pd.pivot_table(data,  values=["bird_id"], index=["behav"], columns=["cluster"], aggfunc=pd.DataFrame.count)
        pivotn = pivot.apply(lambda col: col/col.sum()*100, axis=0) # normalized per column (cluster)
        out[animal] = pivot
        outn[animal] = pivotn
        print(pivot, pivotn)

    panel = pd.Panel.from_dict(out)
    paneln = pd.Panel.from_dict(outn)
    return panel, paneln

if __name__ == "__main__":
    data = "Storks_Africa__10_to_12_2012__with_behav.csv"
    p, pn = compare_behav_types(data)
    p.to_pickle(os.path.join(DATA_ROOT, "out", "compare_behav_types__panel(r=1-max=3h).pkl"))
    pn.to_pickle(os.path.join(DATA_ROOT, "out", "compare_behav_types__panel__normalized(r=1-max=3h).pkl"))
