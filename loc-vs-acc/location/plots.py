import pandas as pd 
pd.options.display.mpl_style = 'default'
import matplotlib.pyplot as plt
import os 

from location import trajectory_processor
from settings import DATA_ROOT

def plot_fpt_std(data_file, min_sampels=2000, plot=True):
    # Load
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, header=None, parse_dates=[2])
    animal_data.columns = ["bird_id", "date", "time", "gps_lat", "gps_long", "behav", "ODBA"]

    animals = animal_data["bird_id"].unique()
    
    radii = [.1, .5, 1, 2, 5, 10, 25]
    out = pd.DataFrame(index=radii, columns=animals)
    print(out)

    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:
            out.drop(animal, inplace=True, axis=1)
            print(out)
            continue 
        tp = trajectory_processor(data, stamp=True).find_best_fpt(radii=radii, plot=False)
        radii, vars = zip(*tp._fpt_diag)
        out[animal] = vars 
        print(out)
     
    if plot:
        out.plot(style="-x")
        plt.xlabel("radius [Km]", fontsize=24)
        plt.ylabel("std(FPT) [h]", fontsize=24)
        plt.xlim([0, max(radii)+1])
        plt.show()
                    
    return out 



    