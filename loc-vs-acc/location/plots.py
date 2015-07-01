import pandas as pd 
import matplotlib as mpl
import matplotlib.pyplot as plt
import os 

from location import trajectory_processor
from settings import DATA_ROOT

pd.options.display.mpl_style = 'default'
mpl.rcParams['axes.facecolor'] = 'w'      # Give me back the white background!
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['lines.linewidth'] = 1
mpl.rcParams['lines.markersize'] = 8
mpl.rcParams['lines.markeredgewidth'] = 1.0
mpl.rcParams['xtick.labelsize'] = 17
mpl.rcParams['ytick.labelsize'] = 17


def copmute_plot_fpt_std(data_file, min_sampels=2000, plot=True, hard_max=3):
    # Load
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, header=None, parse_dates=[2])
    animal_data.columns = ["bird_id", "date", "time", "gps_lat", "gps_long", "behav", "ODBA"]

    animals = animal_data["bird_id"].unique()
    
    radii = [.1, .5, 1, 2, 5, 10, 25]
    out = pd.DataFrame(index=radii, columns=animals)
    
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:
            out.drop(animal, inplace=True, axis=1)            
            continue 
        tp = trajectory_processor(data, stamp=True).find_best_fpt(radii=radii, plot=False, hard_max=hard_max)
        radii, vars = zip(*tp._fpt_diag)
        out[animal] = vars         
     
    if plot:
        plot_fpt_std(out)
                    
    return out 


def plot_fpt_std(data, xmax=21):
    data.plot(color=[(.7, .7, .7)])
    data.mean(axis=1).plot(style="-x", color=(.1, .1, .1), linewidth=3)
    plt.xlabel("radius [Km]", fontsize=28)
    plt.ylabel("std(FPT) [h]", fontsize=28)
    plt.xticks(data.index.values)
    plt.xlim([0, xmax])
    plt.legend().remove()
    plt.show()

def plot_fpt_std_from_csv(file_path, xmax=10):
    data = pd.DataFrame.from_csv(file_path)[:xmax]
    plot_fpt_std(data, xmax+.1)


if __name__ == "__main__":
    file = os.path.join(DATA_ROOT, "out", "fpt-r-var.csv")
    plot_fpt_std_from_csv(file, xmax=10)
