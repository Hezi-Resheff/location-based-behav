
import pandas as pd 
import numpy as np
import os 

from settings import DATA_ROOT


DATA_FILE = os.path.join(DATA_ROOT, "Storks_Africa__10_to_12_2012__with_behav__ALL__FPT.csv")

def time_budgets():
    data = pd.DataFrame.from_csv(DATA_FILE)
    data = data[data.behav > 0] #clean N/A

    #1) print the behav/cluster pivot
    behav_cluster = pd.pivot_table(data,  values=["bird_id"], index=["behav"], columns=["cluster"], aggfunc=pd.DataFrame.count).apply(lambda col: col/col.sum()*100)
    print(behav_cluster)
    print("\n"*2)

    #2) 
    all_birds = data.bird_id.unique()
    for bird in all_birds:
        print("Bird id: {}\n".format(bird) + "="*80)
        data_ = data[data.bird_id == bird]
        c = data_.cluster.value_counts(sort=False) / len(data_)
        c = c.sort_index()
        observed = data_.behav.value_counts(sort=False) / len(data_) * 100
        observed = observed.sort_index()
        expected = np.dot(behav_cluster, c)
        frame = pd.DataFrame([observed.values, expected], columns=observed.index, index=["Observed", "Expected"])
        print(frame)
        print("\n"*2)


if __name__ == "__main__":
    time_budgets()