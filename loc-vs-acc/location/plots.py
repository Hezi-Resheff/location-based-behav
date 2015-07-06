import pandas as pd 
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os 

from location import trajectory_processor, MyBasemap
from settings import DATA_ROOT

pd.options.display.mpl_style = 'default'
mpl.rcParams['axes.facecolor'] = 'w'      # Give me back the white background!
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['lines.linewidth'] = 1
mpl.rcParams['lines.markersize'] = 8
mpl.rcParams['lines.markeredgewidth'] = 1.0
mpl.rcParams['xtick.labelsize'] = 17
mpl.rcParams['ytick.labelsize'] = 17



############# PLot: std(FPT) as f(radius) =============================================================================

def copmute_plot_fpt_std(data_file, min_sampels=2000, plot=True, hard_max=3):
    # Load
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, parse_dates=["stamp"])
    
    animals = animal_data["bird_id"].unique()
    
    radii = [.1, .5, 1, 2, 5, 10, 25]
    out = pd.DataFrame(index=radii, columns=animals)
    
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:
            out.drop(animal, inplace=True, axis=1)            
            continue 
        tp = trajectory_processor(data, stamp=False).find_best_fpt(radii=radii, plot=False, hard_max=hard_max)
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

############# PLot: diluted trajectories ==============================================================================

def compute_plot_trajectories(data_file, min_sampels=2000, plot=True):
    """ return/Plot the diluted version of the trajectories """
    path = os.path.join(DATA_ROOT, data_file)
    animal_data = pd.DataFrame.from_csv(path, parse_dates=["stamp"])
    
    animals = animal_data["bird_id"].unique()
    trajectories = dict()            
    for animal in animals:
        data =  animal_data.loc[animal_data.bird_id == animal].copy()
        print(animal)
        if len(data) < min_sampels:            
            continue         
        trajectories[animal] = trajectory_processor(data, stamp=False).diluted(rad=2.0)

    meta = {
        "mean_lat": animal_data.gps_lat.mean(),
        "mean_lon": animal_data.gps_long.mean(),
        "min_lat": animal_data.gps_lat.min(),
        "min_lon": animal_data.gps_long.min(),
        "max_lat": animal_data.gps_lat.max(),
        "max_lon": animal_data.gps_long.max()
    }

    if plot:
        plot_trajectories(trajectories, meta)

    return trajectories, meta 

def plot_trajectories(data, meta):
    """ The plot for the diluted trajectories """

    params = {
        'projection':'merc', 
        'lat_0': meta["mean_lat"], 
        'lon_0': meta["mean_lon"], 
        'resolution':'h', 
        'area_thresh':0.1, 
        'llcrnrlon': meta["min_lon"]-10, 
        'llcrnrlat': meta["min_lat"]-10, 
        'urcrnrlon': meta["max_lon"]+10, 
        'urcrnrlat': meta["max_lat"]+10, 
    }

    map = MyBasemap(**params)
    map.drawcoastlines()
    map.fillcontinents(color = 'white')
    map.drawmapboundary()          
    map.drawcountries()
    map.printcountries()

        
    #colors = np.linspace(.3, .9, len(data))
    for i, animal in enumerate(data):
        print("Plot: ", animal)
        x, y = map(*data[animal].T)
        map.plot(x, y)
            
    plt.show()



######## Bar plots for per Cluster/Behav stuff ########################################################################

def bar_plot(source, xlabel, ylabel, transpose=True, td=False):
    frame = pd.DataFrame.from_csv(source)
    
    if td:
        frame = frame.applymap(lambda td: pd.Timedelta(td) / np.timedelta64(1, 'D'))
        
    if transpose:
        frame = frame.T
    
    frame.plot(kind='box')
    
    if frame.shape[1] == 3:
        plt.gca().set_xticklabels(['0', '1', '2'])
    else:
        plt.gca().set_xticklabels(['Active Flight', 'Passive Flight', 'Walking', 'Standing', 'Sitting'])

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()





if __name__ == "__main__":
    data_file = "Storks_Africa__10_to_12_2012__with_behav__ALL.csv"
    opt = "marginals"

    if opt == "plot-fpt-r":
        # save data for the r-fpt plot 
        out = copmute_plot_fpt_std(data_file, min_sampels=2000, plot=True, hard_max=3)
        out.to_csv(os.path.join(DATA_ROOT, "out", "fpt-r-var.csv"))

    elif opt == "plot-fpt-r-file":
        file = os.path.join(DATA_ROOT, "out", "fpt-r-var.csv")
        plot_fpt_std_from_csv(file, xmax=10)

    elif opt == "plot-traj":        
        # plot all the trajectories in the data. Just to see that it's al ok... 
        compute_plot_trajectories(data_file)

    elif opt == "marginals":        
        base_path = os.path.join(DATA_ROOT, "out", "marginals")
        plots = (
            ('time.csv', "Cluster", "Total Time (days)", True),
            ('distance_cluster.csv', "Cluster", "Mean Distance", False),            
            ('odba_cluster.csv', "Cluster", "Mean ODBA", False),
            ('odba_behav.csv', "Behavioral Mode", "Mean ODBA", False)
        )
        for path, x, y, td in plots:
            bar_plot(os.path.join(base_path, path), x, y, td=td)

    else:
        print("Nothing to do. Good night :)")

    