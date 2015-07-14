import pandas as pd 
import numpy as np
import os 

from location import trajectory_processor
from settings import DATA_ROOT

def compare_behav_types(data_file, min_sampels=2000, r=1, hard_max=3):

    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, parse_dates=["stamp"])
    
    animal_data.behav = animal_data.behav.replace("\\N", -1).apply(int) # Clean animal behav and add the unknown==-1 style 

    animals = animal_data["bird_id"].unique()
    out = {}
    outn = {} # normalized
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:            
            continue 
        
        data = trajectory_processor(data, stamp=False).compute_first_passage(r, hard_max=hard_max).clean_day_end().cluster("FPT_{}".format(r), k=3)
        pivot = pd.pivot_table(data,  values=["bird_id"], index=["behav"], columns=["cluster"], aggfunc=pd.DataFrame.count)
        pivotn = pivot.apply(lambda col: col/col.sum()*100, axis=0) # normalized per column (cluster)
        out[animal] = pivot
        outn[animal] = pivotn
        print(pivot, pivotn)

    panel = pd.Panel.from_dict(out)
    paneln = pd.Panel.from_dict(outn)
    return panel, paneln


def marginals_etc(data_file, min_sampels=2000, r=1, hard_max=3):
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, parse_dates=["stamp"])
    
    animal_data.behav = animal_data.behav.replace("\\N", -1).apply(int) # Clean animal behav and add the unknown==-1 style 
    animal_data.ODBA = animal_data.ODBA.replace("\\N", np.NaN).apply(float) 

    animals = animal_data["bird_id"].unique()
    
    time = {}
    distance_cluster = {}
    distance_behav = {}
    odba_cluster = {}
    odba_behav = {}
    
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:            
            continue 
        
        data = trajectory_processor(data, stamp=False).compute_steps().compute_first_passage(r, hard_max=hard_max).clean_day_end().cluster("FPT_{}".format(r), k=3)        
                
        time[animal] = data["time"].groupby(data["cluster"]).sum()
        
        distance_cluster[animal] = data["dist"].groupby(data["cluster"]).mean()
        distance_behav[animal] = data["dist"].groupby(data["behav"]).mean()

        odba_cluster[animal] = data["ODBA"].groupby(data["cluster"]).mean()
        odba_behav[animal] = data["ODBA"].groupby(data["behav"]).mean()

        print([d[animal] for d in [time, distance_cluster, distance_behav, odba_cluster, odba_behav]])

    return time, distance_cluster, distance_behav, odba_cluster, odba_behav

def data_with_fpt_mode(data_file, min_sampels=2000, r=1, hard_max=3):
    """ Add the FPT behavioral mode to the entire data """
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, parse_dates=["stamp"])    
    animal_data.behav = animal_data.behav.replace("\\N", -1).apply(int) # Clean animal behav and add the unknown==-1 style 
    animal_data.ODBA = animal_data.ODBA.replace("\\N", np.NaN).apply(float) 
    animals = animal_data["bird_id"].unique()

    def animaliter():
        for animal in animals:
            data =  animal_data.loc[animal_data.bird_id == animal].copy()
            print(animal)
            if len(data) < min_sampels:            
                continue              
            yield data
                    
    frames = [trajectory_processor(data, stamp=False).compute_steps().compute_first_passage(r, hard_max=hard_max).clean_day_end().cluster("FPT_{}".format(r), k=3) 
              for data in animaliter()]

    return pd.concat(frames).reset_index(drop=True)

if __name__ == "__main__":

    data_file = "Storks_Africa__10_to_12_2012__with_behav__ALL.csv"
    opt = "add-fpt-modes"
    
    if opt == "compare-behav":
        # Compare behav types 
        p, pn = compare_behav_types(data_file)    
        p.to_pickle(os.path.join(DATA_ROOT, "out", "compare_behav_types__panel(r=1-max=3h).pkl"))
        pn.to_pickle(os.path.join(DATA_ROOT, "out", "compare_behav_types__panel__normalized(r=1-max=3h).pkl"))

    elif opt == "marginals":
        # Marginals 
        time, distance_cluster, distance_behav, odba_cluster, odba_behav = marginals_etc(data_file)
        # save 
        for p_list in ('time', 'distance_cluster', 'distance_behav', 'odba_cluster', 'odba_behav'):
            pd.DataFrame(eval(p_list)).to_csv(os.path.join(DATA_ROOT, "out", "marginals", "{}.csv".format(p_list)))

    elif opt == "add-fpt-modes":
        data_with_fpt_mode(data_file).to_csv(os.path.join(DATA_ROOT, "Storks_Africa__10_to_12_2012__with_behav__ALL__FPT.csv"))

    else:
        print("Nothing to do. Good night :)")